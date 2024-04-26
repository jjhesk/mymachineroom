class MachineRoomErr(Exception):
    ...


class BadIDs(MachineRoomErr):
    ...


class ServerAuthInfoErr(MachineRoomErr):
    ...


class NodeCountIsNotInPlan(MachineRoomErr):
    ...


class FoundVPNTunnel(MachineRoomErr):
    ...

class DockerAccessProblem(MachineRoomErr):
    ...
