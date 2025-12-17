from flask import Blueprint, render_template, request, jsonify, redirect, flash,current_app,url_for,send_from_directory
from database.connection import SessionLocal
import os
import uuid
from werkzeug.utils import secure_filename
from sqlalchemy import select

bp = Blueprint("personal", __name__, url_prefix="/personal")

@bp.route("/")
def index():
    return render_template("personal/index.html")
