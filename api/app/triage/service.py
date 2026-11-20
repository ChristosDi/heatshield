"""Triage rules: get a suggestion from the AI adapter and keep it pending until a staff member decides.

An approved suggestion re-checks capacity through the centres service before anything is saved.
Django calls triage after a request is saved, so an AI failure can never block saving a request.
"""
