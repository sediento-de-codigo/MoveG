from flask import Blueprint, render_template, session, redirect, url_for
from utils import login_required

viajes_bp = Blueprint("viajes", __name__)
