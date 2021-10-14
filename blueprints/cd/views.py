from flask import Blueprint, render_template, redirect, url_for, request, flash, session, g

from .. auth import login_required

bp = Blueprint('cd', __name__, template_folder="pages", url_prefix="/cd")


@bp.route('/')
@login_required
def Home():
    return "CD Home Page"
