"""Base classes for radix-themes components."""
from __future__ import annotations

from typing import Any, Dict, Literal, Optional, Union

from reflex.components import Component
from reflex.components.tags import Tag
from reflex.utils import imports
from reflex.vars import Var

LiteralAlign = Literal["start", "center", "end", "baseline", "stretch"]
LiteralJustify = Literal["start", "center", "end", "between"]
LiteralSpacing = Literal["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
LiteralVariant = Literal["classic", "solid", "soft", "surface", "outline", "ghost"]
LiteralAppearance = Literal["inherit", "light", "dark"]
LiteralGrayColor = Literal["gray", "mauve", "slate", "sage", "olive", "sand", "auto"]
LiteralPanelBackground = Literal["solid", "translucent"]
LiteralRadius = Literal["none", "small", "medium", "large", "full"]
LiteralScaling = Literal["90%", "95%", "100%", "105%", "110%"]
LiteralAccentColor = Literal[
    "tomato",
    "red",
    "ruby",
    "crimson",
    "pink",
    "plum",
    "purple",
    "violet",
    "iris",
    "indigo",
    "blue",
    "cyan",
    "teal",
    "jade",
    "green",
    "grass",
    "brown",
    "orange",
    "sky",
    "mint",
    "lime",
    "yellow",
    "amber",
    "gold",
    "bronze",
    "gray",
]


class CommonMarginProps(Component):
    """Many radix-themes elements accept shorthand margin props."""

    # Margin: "0" - "9"
    m: Optional[Var[LiteralSpacing]] = None

    # Margin horizontal: "0" - "9"
    mx: Optional[Var[LiteralSpacing]] = None

    # Margin vertical: "0" - "9"
    my: Optional[Var[LiteralSpacing]] = None

    # Margin top: "0" - "9"
    mt: Optional[Var[LiteralSpacing]] = None

    # Margin right: "0" - "9"
    mr: Optional[Var[LiteralSpacing]] = None

    # Margin bottom: "0" - "9"
    mb: Optional[Var[LiteralSpacing]] = None

    # Margin left: "0" - "9"
    ml: Optional[Var[LiteralSpacing]] = None


class RadixThemesComponent(Component):
    """Base class for all @radix-ui/themes components."""

    library = "@radix-ui/themes@^2.0.0"

    # "Fake" prop color_scheme is used to avoid shadowing CSS prop "color".
    _rename_props: Dict[str, str] = {"colorScheme": "color"}

    @classmethod
    def create(
        cls,
        *children,
        **props,
    ) -> Component:
        """Create a new component instance.

        Will prepend "RadixThemes" to the component tag to avoid conflicts with
        other UI libraries for common names, like Text and Button.

        Args:
            *children: Child components.
            **props: Component properties.

        Returns:
            A new component instance.
        """
        component = super().create(*children, **props)
        if component.library is None:
            component.library = RadixThemesComponent.model_fields[
                "library"
            ].default
        component.alias = "RadixThemes" + (
            component.tag or component.__class__.__name__
        )
        return component

    @staticmethod
    def _get_app_wrap_components() -> dict[tuple[int, str], Component]:
        return {
            (45, "RadixThemesColorModeProvider"): RadixThemesColorModeProvider.create(),
        }


class Theme(RadixThemesComponent):
    """A theme provider for radix components.

    This should be applied as `App.theme` to apply the theme to all radix
    components in the app with the given settings.

    It can also be used in a normal page to apply specified properties to all
    child elements as an override of the main theme.
    """

    tag: str = "Theme"

    # Whether to apply the themes background color to the theme node. Defaults to True.
    has_background: Optional[Var[bool]] = None

    # Override light or dark mode theme: "inherit" | "light" | "dark". Defaults to "inherit".
    appearance: Optional[Var[LiteralAppearance]] = None

    # The color used for default buttons, typography, backgrounds, etc
    accent_color: Optional[Var[LiteralAccentColor]] = None

    # The shade of gray, defaults to "auto".
    gray_color: Optional[Var[LiteralGrayColor]] = None

    # Whether panel backgrounds are translucent: "solid" | "translucent" (default)
    panel_background: Optional[Var[LiteralPanelBackground]] = None

    # Element border radius: "none" | "small" | "medium" | "large" | "full". Defaults to "medium".
    radius: Optional[Var[LiteralRadius]] = None

    # Scale of all theme items: "90%" | "95%" | "100%" | "105%" | "110%". Defaults to "100%"
    scaling: Optional[Var[LiteralScaling]] = None

    @classmethod
    def create(
        cls,
        *children,
        color_mode: LiteralAppearance | None = None,
        theme_panel: bool = False,
        accent_color: Union[LiteralAccentColor, Var[LiteralAccentColor]] | None = None,
        **props,
    ) -> Component:
        """Create a new Radix Theme specification.

        Args:
            *children: Child components.
            color_mode: Map to appearance prop.
            theme_panel: Whether to include a panel for editing the theme.
            **props: Component properties.

        Returns:
            A new component instance.
        """
        if color_mode is not None:
            props["appearance"] = color_mode
        if theme_panel:
            children = [ThemePanel.create(), *children]
        if not isinstance(accent_color, Var):
            accent_color = Var.create(accent_color)
        props["accent_color"] = accent_color
        return super().create(*children, **props)

    def _get_imports(self) -> imports.ImportDict:
        return imports.merge_imports(
            super()._get_imports(),
            {
                "": [
                    imports.ImportVar(tag="@radix-ui/themes/styles.css", install=False)
                ],
                "/utils/theme.js": [
                    imports.ImportVar(tag="theme", is_default=True),
                ],
            },
        )

    def _render(self, props: dict[str, Any] | None = None) -> Tag:
        tag = super()._render(props)
        tag.add_props(
            css=Var.create(
                "{{...theme.styles.global[':root'], ...theme.styles.global.body}}",
                _var_is_local=False,
            ),
        )
        return tag


class ThemePanel(RadixThemesComponent):
    """Visual editor for creating and editing themes.

    Include as a child component of Theme to use in your app.
    """

    tag: str = "ThemePanel"

    # Whether the panel is open. Defaults to False.
    default_open: Optional[Var[bool]] = None


class RadixThemesColorModeProvider(Component):
    """Next-themes integration for radix themes components."""

    library = "/components/reflex/radix_themes_color_mode_provider.js"
    tag: str = "RadixThemesColorModeProvider"
    is_default: bool = True


theme = Theme.create
theme_panel = ThemePanel.create
