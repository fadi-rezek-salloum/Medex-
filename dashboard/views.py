from stats.utils.admin.general.avg import get_avg_income
from stats.utils.admin.general.income import (
    get_daily_income,
    get_monthly_income,
    get_yearly_income,
)
from stats.utils.admin.users.active import (
    get_daily_active_users,
    get_monthly_active_users,
    get_yearly_active_users,
)
from stats.utils.admin.users.count import get_users_count
from stats.utils.admin.users.new import (
    get_daily_new_users,
    get_monthly_new_users,
    get_yearly_new_users,
)


def dashboard_callback(request, context):

    if not context:
        context = {}

    general = {
        "daily_income": get_daily_income(),
        "monthly_income": get_monthly_income(),
        "yearly_income": get_yearly_income(),
        "avg": get_avg_income(),
    }

    users = {
        "count": get_users_count(),
        "daily_active": get_daily_active_users(),
        "monthly_active": get_monthly_active_users(),
        "yearly_active": get_yearly_active_users(),
        "daily_new": get_daily_new_users(),
        "monthly_new": get_monthly_new_users(),
        "yearly_new": get_yearly_new_users(),
    }

    context.update({"general": general, "users": users})

    return context
