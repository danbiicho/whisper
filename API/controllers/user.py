import os, sys

BASE_DIR = os.path.dirname(os.path.abspath("API"))
sys.path.extend([BASE_DIR])

import jwt
import pymysql
import bcrypt

from flask import Blueprint, jsonify, request
from jsonschema import validate, ValidationError
from connections import db_connector
from my_settings import SECRET_KEY, ALGORITHM
from models import ModelDao

user_app = Blueprint('user', __name__)
model_dao = ModelDao()

@user_app.route('/kakao', methods=['POST'])
def kakao():
    """ kakao 로그인 API

    """
    db = None
    try:
        token = request.headers['Authorization']
        nickname = request.get_json(silent=True).get('nickname', None)

        if not token:
            return jsonify(message="TOKEN_DOES_NOT_EXIST"), 400

        data = request.get('https://kapi.kakao.com/v2/user/me', headers={'Authorization':f'Bearer {token}'})
        kakao_id = data.json()['kakao_id']

        db = db_connector()
        if db is None:
            return jsonify(message="DATABASE_INIT_ERROR"), 500

        kakao_user = model_dao.search_kakao_user(db, kakao_id)
        # 가입된 계정인 경우 로그인 진행
        if kakao_user:
            token = jwt.encode(kakao_user, SECRET_KEY, ALGORITHM)
            return Jsonify(token=token.decode('utf-8'), nickname=nickname), 200
        # 가입되어있지 않은 계정인 경우 회원가입 진행
        elif kakao_user is None:
            db.begin()
            social_id = model_dao.insert_kakao_user(db, kakao_id)
            if nickname:
                kakao_user = model_dao.insert_kakao_into_user(db, social_id, nickname)
                token = jwt.encode(kakao_user, SECRET_KEY, ALGORITHM)
                return Jsonify(token=token.decode('utf-8'), nickname=nickname), 200
            # 닉네임 입력하지 않은 경우 에러처리
            elif nickname is None:
                return jsonify(message="DATA_ERROR"), 400
            db.commit()

    except Exception as e:
        db.rollback()
        return jsonify(message=f"{e}"), 500
    finally:
        if db:
            db.close()

#이메일 회원가입
@user_app.route('/sign-up', methods=['POST'])
def sign_up()
    try:
        db = db_connector()
        data = request.json
        data['password'] = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        db.begin()
        model_dao.create_user(db, data['email'], data['password'], data['nickname'])
        db.commit()
        return '', 200
    
    except Exception as e:
        db.rollback()
        return jsonify(message = f'{e}'), 500
    
    finally:
        if db:
            db.close()

#이메일 중복 확인
@user_app.route('/email', methods=['POST'])
def check_if_email_exist():
    try:
        db = db_connector
        data = request.json

        email = model_dao.search_email(db, data['email'])
        if email:
            return jsonify(message = "EMAIL_ALREADY_EXIST"), 400
        return jsonify(message = "AVAILABLE_EMAIL"), 200
    
    except Exception as e:
        return jsonify(message = f"{e}"), 500

    finally:
        if db:
            db.close()

#닉네임 중복 확인
@user_app.route('/nickname', methods=['POST'])
def check_if_nickname_exist():
    try:
        db = db_connector
        data = request.json
        
        nickname = model_dao.search_nickname(db, data['nickname'])
        if nickname:
            return jsonify(message = "NICKNAME_ALREADY_EXIST"), 400
        return jsonify(message = "AVAILABLE_NICKNAME"), 200
    
    except Exception as e:
        return jsonify(message = f"{e}")

    finally:
        if db:
            db.close()

#이메일 로그인
@user_app.route('/sign-in', methods=['POST'])
def sign_in():
    try:
        db = db_connector
        data = requset.json
        user = model_dao.search_email(db, user['email'])
        
        if email:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
                token = jwt.encode({'id': user['id']}, SECRET_KEY, ALGORITHM)
                return jsonify(token = token), 200
            
            return jsonify(message = "PASSWORD_DOES_NOT_MATCH"), 400
        return jsonify(message = "EMAIL_DOES_NOT_EXIST"), 400

    except Exception as e:
        return jsonify(message = f"{e}")

    finally:
        if db:
            db.close()
