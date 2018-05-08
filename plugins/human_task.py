"""Human Task Airflow Plugin."""

from time import sleep
from datetime import datetime
from flask import Blueprint, redirect, request
from flask_admin import expose
from flask_admin.contrib.sqla import ModelView
from airflow.utils.db import provide_session
from airflow.utils import apply_defaults
from airflow.plugins_manager import AirflowPlugin
from airflow.operators import BaseOperator
from airflow.exceptions import AirflowException
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from flask_login import current_user, login_required


class HumanTaskOperator(BaseOperator):
    """Human Task Operator."""

    """
    :param poll_interval: Time in seconds between database polls.
    :type poll_interval: int
    """

    @apply_defaults
    def __init__(
            self,
            poll_interval=10,
            *args, **kwargs):
        """Constructor."""
        super(HumanTaskOperator, self).__init__(*args, **kwargs)
        self.poll_interval = poll_interval

    @provide_session
    def poll(self, task_id, session=None):
        """Poll for set state."""
        result = session.query(HumanTask) \
            .filter_by(task_id=task_id).one().state
        session.commit()
        session.close()
        print result
        if result is not None:
            if str(result) == 'Completed':
                print 'Human Task Completed'
            elif str(result) == 'Failed':
                print 'Human Task Failed'
                raise AirflowException('Failure')
            return False
        return True

    @provide_session
    def execute(self, context, session=None):
        """Insert task into human_task table."""
        print context
        # Add current time to make task_id unique on retry
        task_id = (
            context[u'task_instance_key_str'] +
            '_' + str(datetime.time(datetime.now()))) \
            .replace('.', '_')
        session.add(HumanTask(task_id=task_id))
        session.commit()
        session.close()
        sleep(self.poll_interval)
        while self.poll(task_id):
            sleep(self.poll_interval)


Base = declarative_base()


class HumanTask(Base):
    """Human Task table."""

    __tablename__ = "human_task"
    task_id = Column(String(50), primary_key=True)
    claimant = Column(String(50))
    state = Column(String(10))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class HumanTaskModelView(ModelView):
    """Human Task admin view."""

    list_template = 'human_task_list.html'
    can_create = False
    can_edit = False
    can_delete = False
    column_display_pk = True
    form_columns = ['task_id', 'claimant', 'state', 'created_at', 'updated_at']
    column_default_sort = 'task_id'

    @provide_session
    def __init__(
        self,
        model,
        session,
        name=None,
        category=None,
        endpoint=None,
        url=None,
        static_folder=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None
    ):
        """Decorated constructor."""
        super(HumanTaskModelView, self).__init__(
            model,
            session,
            name,
            category,
            endpoint,
            url,
            static_folder,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value
        )

    def get_query(self):
        """Override base method."""
        """Refresh from database to avoid returning stale session data.
        See https://github.com/flask-admin/flask-admin/issues/1593
        """
        self.session.expunge_all()
        return super(HumanTaskModelView, self).get_query()

    def get_count_query(self):
        """Override base method."""
        self.session.expunge_all()
        return super(HumanTaskModelView, self).get_count_query()

    @login_required
    @expose('/claim')
    @provide_session
    def claim(self, session=None):
        """Claim task by setting Claimant."""
        # username = current_user.username \
        #     if hasattr(current_user, 'username') else 'Anon'
        username = str(current_user.get_id())
        id = request.args.get('id')
        session.execute("""
            UPDATE human_task
            SET claimant = :username
            WHERE
                task_id = :id AND
                claimant IS NULL AND
                state IS NULL
        """, {'username': username, 'id': id})
        session.commit()
        session.close()
        return redirect('/admin/humantask/')

    @login_required
    @expose('/release')
    @provide_session
    def release(self, session=None):
        """Release task by setting Claimant to None."""
        # username = current_user.username \
        #     if hasattr(current_user, 'username') else 'Anon'
        username = str(current_user.get_id())
        id = request.args.get('id')
        session.execute("""
            UPDATE human_task
            SET claimant = NULL
            WHERE
                task_id = :id AND
                claimant = :username AND
                state IS NULL
        """, {'username': username, 'id': id})
        session.commit()
        session.close()
        return redirect('/admin/humantask/')

    @login_required
    @expose('/complete')
    @provide_session
    def complete(self, session=None):
        """Set stare to Completed."""
        # username = current_user.username \
        #     if hasattr(current_user, 'username') else 'Anon'
        username = str(current_user.get_id())
        id = request.args.get('id')
        session.execute("""
            UPDATE human_task
            SET state = 'Completed'
            WHERE
                task_id = :id AND
                claimant = :username AND
                state IS NULL
        """, {'username': username, 'id': id})
        session.commit()
        session.close()
        return redirect('/admin/humantask/')

    @login_required
    @expose('/fail')
    @provide_session
    def fail(self, session=None):
        """Set task state to Failed."""
        # username = current_user.username \
        #     if hasattr(current_user, 'username') else 'Anon'
        username = str(current_user.get_id())
        id = request.args.get('id')
        session.execute("""
            UPDATE human_task
            SET state = 'Failed'
            WHERE
                task_id = :id AND
                claimant = :username AND
                state IS NULL
        """, {'username': username, 'id': id})
        session.commit()
        session.close()
        return redirect('/admin/humantask/')


human_task_view = HumanTaskModelView(
    model=HumanTask,
    category="Human Task",
    name="HumanTask"
)

human_task_bp = Blueprint(
    "human_task_bp",
    __name__,
    template_folder="templates/human_task",
    static_folder="static",
    static_url_path="/static/human_task"
)


class AirflowHumanTaskPlugin(AirflowPlugin):
    """Defining the plugin class."""

    name = "HumanTask"
    operators = [HumanTaskOperator]
    flask_blueprints = [human_task_bp]
    hooks = []
    executors = []
    admin_views = [human_task_view]
    menu_links = []
