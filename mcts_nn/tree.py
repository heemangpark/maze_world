import networkx as nx

from env.maze_func import get_avail_action
from env.maze_env import get_mask
from mcts_nn.tree_functions import mask4tree, expand, children, select, backup


class Tree:
    def __init__(self, env, agent):
        self.env = env
        self.agent = agent
        self.args = env.args
        self.g = nx.DiGraph()
        self.g.add_node(1, state=self.env.start_loc, visited=1, Q=0)
        self.state_seq, self.act_seq = None, None

    def grow(self, max_step=500):
        step = 1
        while True:
            idx = 1
            act_seq = []
            state_seq = []

            """selection"""
            while len(children(self.g, idx)) != 0:
                idx, a = select(self.g, idx, c=10)
                act_seq.append(a)
                curr_state = list(self.g.nodes[idx]['state'])
                state_seq.append(curr_state)

            self.state_seq = state_seq
            self.act_seq = act_seq

            """terminal check on selected leaf"""
            if all(self.env.goal_loc == self.g.nodes[idx]['state']):
                break
            else:
                pass

            """expansion"""
            curr_state = self.g.nodes[idx]['state']
            leaves = expand(self.g, idx, avail_actions=get_avail_action(self.env.maze, curr_state))

            """backup"""
            for leaf in leaves:
                self.env.ag_loc = self.g.nodes[leaf]['state']
                dist_to_goal = abs(self.env.ag_loc - self.env.goal_loc).sum()
                if dist_to_goal == 0:
                    leaf_r = 10
                elif dist_to_goal == 1:
                    leaf_r = 0
                else:
                    leaf_r = -1
                mask = mask4tree(self.env.maze, self.env.ag_loc)
                leaf_q = self.agent.step(self.env.convert_maze_to_g_loc(), mask, tree_search=True)
                backup(self.g, leaf, leaf_r, leaf_q)

            step += 1
            if step >= max_step:
                break

            # """visualize per step"""
            # if step % 50 == 0:
            #     vis_route(self.env.maze, self.state_seq, self.env.start_loc, self.env.goal_loc, step)
