from stats.utils.admin.general.avg import get_avg_income
from stats.utils.admin.general.income import (
    get_daily_income,
    get_monthly_income,
    get_yearly_income,
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

    context.update({"general": general})

    return context
