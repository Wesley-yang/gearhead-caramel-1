from . import plotutility
import random
import pbge
from pbge.plots import Plot, PlotState
import gears

DG_NAME = "DG_NAME"
DG_ARCHITECTURE = "DG_ARCHITECTURE"
DG_SCENE_TAGS = "DG_SCENE_TAGS"
DG_MONSTER_TAGS = "DG_MONSTER_TAGS"
DG_TEMPORARY = "DG_TEMPORARY"
DG_PARENT_SCENE = "DG_PARENT_SCENE"


def dungeon_cleaner(scene):
    # Vacuum up all the dead monsters.
    for bit in list(scene.contents):
        if hasattr(bit, "is_operational") and not bit.is_operational():
            scene.contents.remove(bit)


class ProtoDLevel(object):
    def __init__(self, parent, depth, branch=0, gen="DUNGEON_GENERIC", terminal=False):
        self.depth = depth
        self.branch = branch
        self.gen = gen
        self.terminal = terminal
        self.parent = parent
        self.real_scene = None

    BRANCH_IDENTIFIERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    def get_name(self, base_name):
        if self.branch == 0:
            return "{}, Level {}".format(base_name, self.depth)
        else:
            return "{}, Level {}{}".format(base_name, self.depth, self.BRANCH_IDENTIFIERS[self.branch - 1])


class DungeonMaker(object):
    # Create a set of dungeon levels. Connect them to one another.
    # Will set goal_level and entry_level. The entry_level scene has no entrance; need to make one.
    def __init__(self, nart, parent_plot: Plot, parent_scene, name, architecture, rank,
                 scene_tags=(gears.tags.SCENE_DUNGEON, gears.tags.SCENE_SEMIPUBLIC), monster_tags=(),
                 temporary=False,
                 connector=plotutility.StairsDownToStairsUpConnector,
                 goal_room=None, goal_item=None):
        self.name = name
        self.architecture = architecture
        self.rank = rank
        self.connector = connector
        self.proto_levels = list()
        self.hi_branch = 0

        self.add_a_level(None, 1, 0)

        r_levels = list(self.proto_levels)
        random.shuffle(r_levels)
        self.goal_proto_level = max(r_levels, key=lambda l: l.depth)

        for proto in self.proto_levels:
            if proto.parent and proto.parent.real_scene:
                parent = proto.parent.real_scene
            else:
                parent = parent_scene
            sp = parent_plot.add_sub_plot(nart, proto.gen, spstate=PlotState(rank=rank + proto.depth * 3, elements={
                DG_NAME: proto.get_name(name), DG_ARCHITECTURE: architecture, DG_TEMPORARY: temporary,
                DG_SCENE_TAGS: scene_tags, DG_MONSTER_TAGS: monster_tags, DG_PARENT_SCENE: parent
            }))
            proto.real_scene = sp.elements["LOCALE"]
            if proto.terminal:
                sp.add_sub_plot(nart, "DUNGEON_GOAL")
            if parent and parent is not parent_scene:
                connector(parent_plot, parent, proto.real_scene, )
            else:
                self.entry_level = proto.real_scene

        self.goal_level = self.goal_proto_level.real_scene

    def add_a_level(self, parent, depth, branch):
        mylevel = ProtoDLevel(parent, depth, branch)
        self.proto_levels.append(mylevel)
        if random.randint(2, 6) > min(depth, 5):
            # Add another level.
            if random.randint(1, 5) == 1 and self.hi_branch < 5:
                # Branch this dungeon.
                self.add_a_level(mylevel, depth + 1, self.hi_branch + 1)
                self.add_a_level(mylevel, depth + 1, branch)
                self.hi_branch += 1
            else:
                self.add_a_level(mylevel, depth + 1, branch)
        else:
            mylevel.terminal = True
