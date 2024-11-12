import django.contrib.sessions.backends.db as db

class SessionStore(db.SessionStore):
    session_counter = 0

    def _get_new_session_key(self):
        session_key = "logincookie-0"
        while self.exists(session_key):
            session_key = "logincookie-" + str(SessionStore.session_counter)
            SessionStore.session_counter += 1

        return session_key