from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g
import functools

from .. auth import login_required
from .. DB import get_db

from .dataclass import Options

bp = Blueprint('options', __name__, template_folder="pages", url_prefix="/options")

@bp.route('/')
def Home():
    return "Option Home"


@bp.route("/company")
def Company():
    return "Company"


@bp.route("/cd")
def CD():
    return "CD signatories"


