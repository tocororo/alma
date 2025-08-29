import re 

onei_regexp = re.compile(r"^https:\/\/onei\.gob\.cu\/[a-zA-Z]+\/\d+$")

def get_onei_scheme_config():
    return {
            # See examples in `idutils.validators` file.
            "validator": onei_validator,
            # Used in `idutils.normalizers.normalize_pid` function.
            "normalizer": lambda value: normalized_value,
            # See examples in `idutils.detectors.IDUTILS_SCHEME_FILTER` config.
            "filter": [],
            # Used in `idutils.normalizers.to_url` function.
            "url_generator": normalized_value,
        }

def onei_validator(val):   
    return onei_regexp.match(val)

def normalized_value(val):
    return val