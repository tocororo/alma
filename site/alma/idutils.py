


def get_onei_scheme_config():
    return {
            # See examples in `idutils.validators` file.
            "validator": onei_validator,
            # Used in `idutils.normalizers.normalize_pid` function.
            "normalizer": lambda value: normalized_value,
            # See examples in `idutils.detectors.IDUTILS_SCHEME_FILTER` config.
            "filter": ["list_of_schemes_to_filter_out"],
            # Used in `idutils.normalizers.to_url` function.
            "url_generator": lambda scheme, normalized_pid: "normalized_url",
        }

def onei_validator(val):
    pass
def normalized_value(val):
    pass