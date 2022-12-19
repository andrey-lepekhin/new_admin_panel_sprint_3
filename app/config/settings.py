from split_settings.tools import optional, include

include(
    'components/common.py',
    'components/database.py',
    optional('components/local.py'),
)
