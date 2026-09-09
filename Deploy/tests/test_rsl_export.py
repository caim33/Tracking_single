"""Optional real RSL-RL CPU checks, without claiming an Isaac or robot rollout.

Requires Torch >=2.7 and rsl-rl-lib==3.0.1 (the train extra in an Isaac environment).
Synthetic observations exercise the optimizer and exporter, not motion quality.
"""
import ast
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import pytest

torch = pytest.importorskip('torch')
pytest.importorskip('rsl_rl')
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from tensordict import TensorDict
from Deploy.export import export_bundle
from Deploy.runtime import OBSERVATIONS, TrackingPolicy


def settings(name):
    """Use the retained task's actual MLP/PPO parameters without importing Isaac."""
    root = Path(__file__).resolve().parents[2]
    path = root/'RL_envs/source/WBC/WBC/tasks/manager_based/tracking_single/agents/rsl_rl_ppo_cfg.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == name for target in node.targets))
    return {kw.arg: ast.literal_eval(kw.value) for kw in assignment.value.keywords}


@pytest.fixture(autouse=True)
def cpu_threads():
    old = torch.get_num_threads()
    torch.set_num_threads(1)
    torch.manual_seed(7)
    yield
    torch.set_num_threads(old)


def observations(count):
    return TensorDict({'policy': torch.randn(count, 154), 'critic': torch.randn(count, 286)}, batch_size=[count])


def test_real_rsl_ppo_updates_with_retained_config():
    obs = observations(4)
    policy = ActorCritic(obs, {'policy': ['policy'], 'critic': ['critic']}, 29, **settings('policy'))
    optimizer = PPO(policy, device='cpu', **settings('algorithm'))
    optimizer.init_storage('rl', 4, 8, obs, [29])
    before = next(policy.actor.parameters()).detach().clone()
    with torch.inference_mode():
        for _ in range(8):
            action = optimizer.act(obs)
            obs = observations(4)
            optimizer.process_env_step(obs, -action.square().mean(dim=-1), torch.zeros(4), {})
        optimizer.compute_returns(obs)
    losses = optimizer.update()
    assert all(np.isfinite(value) for value in losses.values()), losses
    assert not torch.equal(before, next(policy.actor.parameters()))


@pytest.mark.parametrize('normalized', [False, True])
def test_real_rsl_bundle_export_matches_torch(tmp_path, motion, normalized):
    obs = observations(8)
    config = settings('policy')
    config['actor_obs_normalization'] = normalized
    policy = ActorCritic(obs, {'policy': ['policy'], 'critic': ['critic']}, 29, **config)
    if normalized:
        policy.update_normalization(obs)
    policy.eval()
    names = list(motion['joint_names'])
    default_q = torch.tensor(motion['joint_pos'][:1])
    robot = SimpleNamespace(joint_names=names, data=SimpleNamespace(
        default_joint_pos=default_q, default_joint_vel=torch.zeros(1, 29),
        joint_stiffness=torch.full((1, 29), 50.), joint_damping=torch.full((1, 29), 2.),
        joint_effort_limits=torch.full((1, 29), 30.)))
    action = SimpleNamespace(_scale=torch.full((1, 29), 0.1), _offset=default_q.clone())
    env = SimpleNamespace(scene={'robot': robot}, step_dt=0.02,
                          action_manager=SimpleNamespace(get_term=lambda name: action),
                          observation_manager=SimpleNamespace(active_terms={'policy': [name for name, _ in OBSERVATIONS]}),
                          cfg=SimpleNamespace(commands=SimpleNamespace(motion=SimpleNamespace(anchor_body_name='torso_link'))))
    source = tmp_path/'motion.npz'
    np.savez_compressed(source, **motion)
    output = tmp_path/'bundle'
    export_bundle(env, SimpleNamespace(alg=SimpleNamespace(policy=policy)), source, output,
                  'G1-Tracking-Dance-demo', None)
    deployed = TrackingPolicy(output)
    target, obs_array = deployed.step(0, default_q[0].numpy(), np.zeros(29), np.zeros(3),
                                      motion['body_quat_w'][0, deployed.anchor])
    with torch.inference_mode():
        expected = policy.act_inference(TensorDict({'policy': torch.from_numpy(obs_array[None])}, batch_size=[1]))[0].numpy()
    assert np.max(abs(expected)) > 1e-4
    np.testing.assert_allclose(target, default_q[0].numpy() + 0.1*expected, atol=1e-5, rtol=1e-5)
