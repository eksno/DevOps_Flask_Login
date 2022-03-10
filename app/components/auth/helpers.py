import random

from app.components.auth import model


def get_apiauth_object_by_ip(ip):
    """
    Query the datastorage for an API key.
    @param ip: ip address
    @return: apiauth sqlachemy object.
    """
    return model.APIAuth.query.filter_by(ip=ip).first()


def get_apiauth_object_by_key(key):
    """
    Query the datastorage for an API key.
    @param ip: ip address
    @return: apiauth sqlachemy object.
    """
    return model.APIAuth.query.filter_by(key=key).first()


def get_apiauth_object_by_keyid(keyid):
    """
    Query the datastorage for an API key.
    @param ip: ip address
    @return: apiauth sqlachemy object.
    """
    return model.APIAuth.query.filter_by(id=keyid).first()


def get_all_apiauth_object():
    """
    Query the datastorage for all API keys.
    @param ip: ip address
    @return: apiauth sqlachemy object.
    """
    return model.APIAuth.query.all()


def generate_hash_key():
    """
    @return: .
    """
    pass
