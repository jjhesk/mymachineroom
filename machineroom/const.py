class CKB:
    REMOTE_WS: str = "...remote_locator"
    RAM_GB_REQUIREMENT: int = 4
    DISK_GB_REQUIREMENT: int = 100


class PROJECT2:
    K1_STR: str
    K2_STR: str
    K3_STR: str
    K4_STR: str
    K5_STR: str
    V1_INT: int
    V2_INT: int
    V3_INT: int
    V4_INT: int
    V5_INT: int
    V1_FLOAT: float
    V2_FLOAT: float
    V3_FLOAT: float
    V4_FLOAT: float
    V5_FLOAT: float


class Config(CKB, PROJECT2):
    DATAPATH_BASE: str = "...._file....locator"
    TEMP_FILE: str = "tmp.txt"
    TEMP_JS: str = "tmp.js"
    PUB_KEY: str = "/Users/xxxx/.ssh/id_rsa.pub"
    LOCAL_KEY_HOLDER: str = "/Users/xxxx/.ssh"
    MY_KEY_FEATURE: str = "xxx@xxxx"
    HOME: str = "/root"
    DOCKER_COMPOSE_VERSION: str = "2.24.6"
