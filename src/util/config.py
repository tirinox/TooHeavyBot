import yaml
import sys
from util.singleton import Singleton
from util.date import parse_timespan_to_seconds
import os


def error(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)


class ConfigSubtree:
    def __init__(self, config=None):
        self.config = config or {}

    def set_property(self, key, v):
        self.config[key] = v

    def get(self, path: str = '', default=None):
        subtree = self.config

        components = path.strip().split('.', maxsplit=16)

        for component in components:
            if type(subtree) is dict:
                if component in subtree:
                    subtree = subtree[component]
                else:
                    return default
            else:
                return default

        return subtree

    def get_inteval_seconds(self, path, default=None, min_interval=None, max_interval=None):
        v = self.get(path, default)
        result = parse_timespan_to_seconds(v)

        if type(result) is str:
            raise ValueError('Config parse error! {}'.format(result))

        min_interval_sec = parse_timespan_to_seconds(min_interval) if type(min_interval) is str else min_interval
        if min_interval is not None and result < min_interval_sec:
            raise ValueError('Config entry with name {} = {} < {}!'.format(path,
                                                                           v,
                                                                           min_interval))

        max_interval_sec = parse_timespan_to_seconds(max_interval) if type(max_interval) is str else max_interval
        if max_interval is not None and result > max_interval_sec:
            raise ValueError('Config entry with name {} = {} > {}!'.format(path,
                                                                           v,
                                                                           max_interval))

        return result

    def subtree(self, path):
        st = self.get(path)
        if st:
            return ConfigSubtree(st)
        else:
            return None

    def __repr__(self) -> str:
        return 'Config: {!r}'.format(self.config)

    def __getitem__(self, path):
        return self.get(path)


class Config(ConfigSubtree, metaclass=Singleton):
    def __init__(self, default_config_file='.config.yml', config=None):
        super().__init__(config)
        if config is None:
            if len(sys.argv) == 2:
                config_file = sys.argv[1]
            else:
                config_file = default_config_file
                if not os.path.isfile(config_file):
                    config_file = os.path.join(os.path.pardir, config_file)
            self.load(config_file)

    def _load(self, file):
        try:
            with open(file, 'r') as stream:
                self.config = yaml.load(stream, Loader=yaml.SafeLoader)
        except yaml.YAMLError as exc:
            print('Error parsing YAML: {}'.format(exc))

    def load(self, file):
        error('Loading config: {}'.format(file))
        self._load(file)

    @property
    def is_debug(self):
        return bool(self.get('debug', False))
