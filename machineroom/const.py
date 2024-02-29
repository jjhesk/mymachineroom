class CKB:
    REMOTE_WS: str = "...remote_locator"
    RAM_GB_REQUIREMENT: str = 4


class Config(CKB):
    DATAPATH_BASE: str = "...._file....locator"
    TEMP_FILE: str = "tmp.txt"
    TEMP_JS: str = "tmp.js"
    PUB_KEY: str = "/Users/xxxx/.ssh/id_rsa.pub"
    LOCAL_KEY_HOLDER: str = "/Users/xxxx/.ssh"
    MY_KEY_FEATURE: str = "xxx@xxxx"
    HOME: str = "/root"
    DOCKER_COMPOSE_VERSION: str = "2.24.6"
