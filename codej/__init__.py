import jinja2
import typing

import redis.asyncio as redis

from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.routing import Mount, Route
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.types import Receive, Scope, Send
from starlette.templating import Jinja2Templates
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import assets

from .dirs import base, static, templates, settings
from .errors import show_error
from .announces.views import show_announce, show_announces
from .aliases.views import show_aliases
from .api.announces import Announce, Announces, Broadcast
from .api.aliases import Aliases
from .api.arts import Art, Arts, Dislike, Lenta, Like
from .api.auth import (
    ChangeAva, ChangeEmail, ChangePasswd, GetPasswd,
    Login, Logout, LogoutAll, ResetPasswd,
    RequestEm, SetPasswd)
from .api.drafts import Draft, Drafts, Labels, Paragraph
from .api.main import Captcha, Index
from .api.people import People, Profile, Relation
from .api.pictures import Album, Albums, Albumstat, Picstat, Search, Ustat
from .api.tasks import check_swapped, rem_expired_sessions
from .arts.views import show_art, show_arts
from .captcha.views import show_captcha
from .drafts.views import show_draft, show_drafts, show_labeled
from .main.views import (
    jump, show_avatar, show_favicon, show_index,
    show_picture, show_public, show_sitemap)
from .people.views import show_people, show_profile
from .pictures.views import show_album, show_albums

try:
    from .tuning import SECRET_KEY, SITE_NAME, SITE_DESCRIPTION, MAIL_PASSWORD
    if MAIL_PASSWORD:
        settings.file_values['MAIL_PASSWORD'] = MAIL_PASSWORD
    if SECRET_KEY:
        settings.file_values['SECRET_KEY'] = SECRET_KEY
    if SITE_NAME:
        settings.file_values['SITE_NAME'] = SITE_NAME
    if SITE_DESCRIPTION:
        settings.file_values['SITE_DESCRIPTION'] = SITE_DESCRIPTION
except ModuleNotFoundError:
    pass

DI = '''typing.Union[str, os.PathLike[typing.AnyStr],
typing.Sequence[typing.Union[str,
os.PathLike[typing.AnyStr]]]]'''.replace('\n', ' ')


class J2Templates(Jinja2Templates):
    def _create_env(
            self,
            directory: DI, **env_options: typing.Any) -> "jinja2.Environment":
        loader = jinja2.FileSystemLoader(directory)
        assets_env = AssetsEnvironment(static, '/static')
        assets_env.debug = settings.get('ASSETS_DEBUG', bool)
        env_options.setdefault("loader", loader)
        env_options.setdefault("autoescape", True)
        env_options.setdefault("extensions", [assets])
        env = jinja2.Environment(**env_options)
        env.assets_environment = assets_env
        return env


class StApp(Starlette):
    async def __call__(
            self, scope: Scope, receive: Receive, send: Send) -> None:
        scope["app"] = self
        self.config = settings
        self.jinja = J2Templates(directory=templates)
        self.rp = redis.ConnectionPool.from_url(
            settings.get('REDI'),
            health_check_interval=30,
            socket_connect_timeout=15,
            socket_keepalive=True,
            retry_on_timeout=True,
            decode_responses=True)
        if self.middleware_stack is None:
            self.middleware_stack = self.build_middleware_stack()
        await self.middleware_stack(scope, receive, send)


async def run_before():
    await rem_expired_sessions(settings)
    await check_swapped(settings)


middleware = [
    Middleware(
        SessionMiddleware,
        secret_key=settings('SECRET_KEY'),
        max_age=settings.get('SESSION_LIFETIME', cast=int))]

errs = {404: show_error}

app = StApp(
    debug=settings.get('DEBUG', cast=bool),
    routes=[
        Route('/', show_index, name='index'),
        Route('/favicon.ico', show_favicon, name='favicon'),
        Route('/sitemap.xml', show_sitemap, name='sitemap'),
        Route('/{suffix}', jump, name='jump'),
        Route('/ava/{username}/{size:int}', show_avatar, name='ava'),
        Route('/captcha/{suffix}', show_captcha, name='captcha'),
        Route('/picture/{suffix}', show_picture, name='picture'),
        Route('/public/{slug}', show_public, name='public'),
        Mount('/announces', name='announces', routes=[
            Route('/', show_announces, name='announces'),
            Route('/{suffix}', show_announce, name='announce')]),
        Mount('/aliases', name='aliases', routes=[
            Route('/', show_aliases, name='aliases')]),
        Mount('/api', name='api', routes=[
            Route('/index', Index, name='aindex'),
            Route('/captcha', Captcha, name='acaptcha'),
            Route('/login', Login, name='alogin'),
            Route('/logout', Logout, name='alogout'),
            Route('/logoutall', LogoutAll, name='alogoutall'),
            Route('/request-reg', GetPasswd, name='agetpasswd'),
            Route('/reset-passwd', ResetPasswd, name='aresetpwd'),
            Route('/setpasswd', SetPasswd, name='asetpwd'),
            Route('/profile', Profile, name='aprofile'),
            Route('/change-ava', ChangeAva, name='chava'),
            Route('/change-passwd', ChangePasswd, name='chpwd'),
            Route('/request-email-change', RequestEm, name='reemchange'),
            Route('/change-email', ChangeEmail, name='change-email'),
            Route('/rel', Relation, name='arel'),
            Route('/people', People, name='apeople'),
            Route('/aliases', Aliases, name='aaliases'),
            Route('/pictures', Albums, name='aalbums'),
            Route('/pictures/{suffix}', Album, name='aalbum'),
            Route('/albumstat', Albumstat, name='albumstat'),
            Route('/ustat', Ustat, name='austat'),
            Route('/picstat', Picstat, name='apicstat'),
            Route('/search', Search, name='asearch'),
            Route('/drafts', Drafts, name='adrafts'),
            Route('/draft', Draft, name='adraft'),
            Route('/labels', Labels, name='alabel'),
            Route('/send-par', Paragraph, name='aparagraph'),
            Route('/art', Art, name='aart'),
            Route('/arts', Arts, name='aarts'),
            Route('/follow', Lenta, name='afollow'),
            Route('/like', Like, name='alike'),
            Route('/dislike', Dislike, name='adislike'),
            Route('/announces', Announces, name='aannounces'),
            Route('/announce', Announce, name='aannounce'),
            Route('/broadcast', Broadcast, name='abroadcast'),
            ]),
        Mount('/arts', name='arts', routes=[
            Route('/', show_arts, name='arts'),
            Route('/{slug}', show_art, name='art')
            ]),
        Mount('/drafts', name='drafts', routes=[
            Route('/', show_drafts, name='drafts'),
            Route('/{slug}', show_draft, name='draft'),
            Route('/t/{label}', show_labeled, name='show-labeled')]),
        Mount('/people', name='people', routes=[
            Route('/', show_people, name='people'),
            Route('/{username}', show_profile, name='profile')]),
        Mount('/pictures', name='pictures', routes=[
            Route('/', show_albums, name='albums'),
            Route('/{suffix}', show_album, name='album')]),
        Mount('/static', app=StaticFiles(directory=static), name='static')],
    on_startup=[run_before],
    middleware=middleware,
    exception_handlers=errs)
