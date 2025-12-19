from __future__ import annotations

import logging
import re
import sys
import time
import traceback
from pathlib import Path
from typing import TYPE_CHECKING

import reflex as rx
from reflex.plugins import Plugin
from reflex.plugins.base import Plugin as BasePlugin
from reflex.state import FrontendEventExceptionState
from reflex.vars.base import Var

if TYPE_CHECKING:
    from typing import Unpack

    from reflex.app import App
    from reflex.plugins.base import PostCompileContext
    from starlette.requests import Request
    from starlette.responses import Response

original_flush = sys.stdout.flush


def flush(*args: object, **kwargs: object):
    sys.stdout.write("\03")
    return original_flush(*args, **kwargs)


sys.stdout.flush = flush

if hasattr(FrontendEventExceptionState, "auto_reload_on_errors"):
    FrontendEventExceptionState.auto_reload_on_errors.append(
        re.compile(
            re.escape("TypeError: can't access property \"")
            + r".*"
            + re.escape('", ')
            + r".*"
            + re.escape(" is null")
        )
    )

PIXEL_SCRIPT_POSTHOG: str = """
try {
    if (!globalThis._posthog_init) {
        globalThis._posthog_init = true;
        ! function(t, e) {
            var o, n, p, r;
            e.__SV || (window.posthog = e, e._i = [], e.init = function(i, s, a) {
                function g(t, e) {
                    var o = e.split(".");
                    2 == o.length && (t = t[o[0]], e = o[1]), t[e] = function() {
                        t.push([e].concat(Array.prototype.slice.call(arguments, 0)))
                    }
                }(p = t.createElement("script")).type = "text/javascript", p.async = !0, p.src = s.api_host.replace(".i.posthog.com", "-assets.i.posthog.com") + "/static/array.js", (r = t.getElementsByTagName("script")[0]).parentNode.insertBefore(p, r);
                var u = e;
                for (void 0 !== a ? u = e[a] = [] : a = "posthog", u.people = u.people || [], u.toString = function(t) {
                        var e = "posthog";
                        return "posthog" !== a && (e += "." + a), t || (e += " (stub)"), e
                    }, u.people.toString = function() {
                        return u.toString(1) + ".people (stub)"
                    }, o = "capture identify alias people.set people.set_once set_config register register_once unregister opt_out_capturing has_opted_out_capturing opt_in_capturing reset isFeatureEnabled onFeatureFlags getFeatureFlag getFeatureFlagPayload reloadFeatureFlags group updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures getActiveMatchingSurveys getSurveys getNextSurveyStep onSessionId setPersonProperties".split(" "), n = 0; n < o.length; n++) g(u, o[n]);
                e._i.push([i, s, a])
            }, e.__SV = 1)
        }(document, window.posthog || []);
        posthog.init('reflex_pixel_id', {
            api_host: 'https://us.i.posthog.com',
            person_profiles: 'always',
            session_recording: {
                recordCrossOriginIframes: true,
            },
            custom_campaign_params: ["utm_post_id", "utm_influencer"],
        });
    }
} catch (error) {
    // Silently fail if PostHog initialization fails
    console.debug('PostHog initialization failed silently');
}
"""
REFLEX_PIXEL_ID: str = "phc_A0MAR0wCGhXrizWmowRZcYqyZ8PMhPPQW06KEwD43aC"


def get_pixel_script_posthog(
    reflex_pixel_id: str,
) -> str:
    """Get the PostHog pixel script."""
    return PIXEL_SCRIPT_POSTHOG.replace(
        "reflex_pixel_id",
        reflex_pixel_id,
    )


def get_pixel_website_trackers() -> rx.Component:
    """Get the website trackers."""
    return rx.script(
        get_pixel_script_posthog(
            reflex_pixel_id=REFLEX_PIXEL_ID,
        ),
    )


class WindowMessageListener(rx.Fragment):
    def add_imports(self) -> rx.ImportDict:
        return {
            "react-router": rx.ImportVar("useLocation"),
            "react": rx.ImportVar("useEffect"),
        }

    def add_hooks(self) -> list[str | Var[object]]:
        return [
            "const location = useLocation();",
            r"""
useEffect(() => {
  window.parent.postMessage(
    { __reflex_iframe_event: { _type: "loaded" } },
    "*"
  );
}, [])""",
            r"""
useEffect(() => {
  window.parent.postMessage(
    {
      __reflex_iframe_event: {
        _type: "navigation",
        data: { path: location.pathname, search: location.search },
      },
    },
    "*"
  );
}, [location.pathname, location.search]);
""",
        ]


class ErrorPrefixFormatter(logging.Formatter):
    """Formatter that adds ERROR: prefix to error-level logs."""

    def format(self, record):  # noqa: ANN001
        formatted_message = super().format(record)

        if record.levelno >= logging.ERROR:
            return f"[ERROR]: {formatted_message}"

        return formatted_message


class FlexgenStreamHandler(logging.StreamHandler):
    """Custom StreamHandler with ErrorPrefixFormatter for Flexgen logging."""

    def __init__(self, stream=None):  # noqa: ANN001
        super().__init__(stream or sys.stdout)
        formatter = ErrorPrefixFormatter("%(name)s - %(levelname)s - %(message)s")
        self.setFormatter(formatter)


def set_logger():
    root_logger = logging.getLogger()

    # Check if FlexgenStreamHandler already exists
    for handler in root_logger.handlers:
        if isinstance(handler, FlexgenStreamHandler):
            return

    # Add our custom handler if it doesn't exist
    handler = FlexgenStreamHandler()
    root_logger.addHandler(handler)


class LogModPlugin(Plugin):
    def __init__(self):
        set_logger()


CREATE_STATE = "/_create_state"


class CreateStatePlugin(BasePlugin):
    def post_compile(self, **context: Unpack[PostCompileContext]) -> None:
        """Called after the compilation of the plugin.

        Args:
            context: The context for the plugin.
        """
        app = context["app"]
        self._create_state_endpoint(app)

    @staticmethod
    def _create_state_endpoint(app: App) -> None:
        """Add an endpoint to the app that creates a new state.

        Args:
            app: The application instance to which the endpoint will be added.
        """
        if not app._api:
            return

        async def create_state(request: Request) -> Response:
            import uuid

            from reflex.state import _substate_key
            from starlette.responses import JSONResponse

            try:
                if not app.event_namespace:
                    return JSONResponse({})

                state_name_to_values: dict[
                    str, dict[str, object]
                ] = await request.json()

                if not isinstance(state_name_to_values, dict):
                    return JSONResponse(
                        {"error": "State name to values must be a dictionary."},
                        status_code=400,
                    )

                for key, value in state_name_to_values.items():
                    if not isinstance(key, str) or not isinstance(value, dict):
                        return JSONResponse(
                            {
                                "error": "State name to values must be a dictionary of string to dictionary."
                            },
                            status_code=400,
                        )
                    for sub_key in value:
                        if not isinstance(sub_key, str):
                            return JSONResponse(
                                {
                                    "error": "State name to values must be a dictionary of string to dictionary of string to value."
                                },
                                status_code=400,
                            )

                classes_to_process = [app._state] if app._state else []
                classes = classes_to_process.copy()
                while classes_to_process:
                    cls = classes_to_process.pop()
                    for subclass in cls.class_subclasses:
                        if subclass not in classes:
                            classes.append(subclass)
                            classes_to_process.append(subclass)

                names_to_classes = {cls.__name__: cls for cls in classes}

                all_states = [
                    cls(
                        parent_state=None,
                        _reflex_internal_init=True,
                        init_substates=False,
                    )
                    for cls in classes
                ]

                for state in all_states:
                    cls = type(state)
                    payload = (
                        state_name_to_values.get(cls.__name__, {})
                        if names_to_classes[cls.__name__] is cls
                        else {}
                    )
                    for key, value in payload.items():
                        setattr(state, key, value)

                for state in all_states:
                    for potential_substate in all_states:
                        if (
                            potential_substate is not state
                            and type(potential_substate) in state.class_subclasses
                        ):
                            state.substates[potential_substate.get_name()] = (
                                potential_substate
                            )
                            potential_substate.parent_state = state

                new_token = uuid.uuid4().hex

                await app.state_manager.set_state(
                    _substate_key(new_token, all_states[0]), all_states[0]
                )

                return JSONResponse(new_token)
            except Exception as e:
                return JSONResponse(
                    {
                        "error": "Internal server error.",
                        "error_message": str(e),
                        "traceback": traceback.format_exc(),
                    },
                    status_code=500,
                )

        app._api.add_route(
            CREATE_STATE,
            create_state,
            methods=["POST"],
        )


LAST_COMPILED_FILE = Path("/home/user/.last_compiled")


class WriteToLastCompiledPlugin(BasePlugin):
    def post_compile(self, **context: Unpack[PostCompileContext]) -> None:
        """Called after the compilation of the plugin.

        Args:
            context: The context for the plugin.
        """
        LAST_COMPILED_FILE.write_text(str(time.time()))


@rx.memo
def injected_component():
    return rx.fragment(
        WindowMessageListener.create(),
        get_pixel_website_trackers(),
    )
