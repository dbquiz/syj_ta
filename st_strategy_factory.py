from st_thestrat import TheStrat
from st_zindex import ZIndex
from st_cci_bo import CCIBO
#===========================================

class StrategyFactory:
    _strategies = [
        (str(TheStrat()), TheStrat()),
        (str(ZIndex()), ZIndex()),
        (str(CCIBO()), CCIBO()),
    ]

    @classmethod
    def list_descriptions(cls):
        return [desc for desc, _ in cls._strategies]

    @classmethod
    def get_instance_by_description(cls, description):
        for desc, instance in cls._strategies:
            if desc == description:
                return instance
        raise ValueError(f"No strategy matches description: {description}")

    @classmethod
    def get_all_instances(cls):
        return [instance for _, instance in cls._strategies]
