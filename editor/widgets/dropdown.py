from editor.widgets.floating_dropdown import draw_dropdown_field, draw_floating_dropdown


def draw_dropdown(
    screen,
    rect,
    label,
    value,
    options,
    action,
    expanded=False,
    select_action="object_category_select",
    option_key="category",
    allow_new=True,
):
    buttons, field_rect = draw_dropdown_field(screen, rect, label, value, action)

    if expanded:
        dropdown = draw_floating_dropdown(
            screen,
            field_rect,
            options,
            value,
            select_action,
            option_key,
            allow_new=allow_new,
            new_action="object_category_new",
        )
        buttons.extend(dropdown["buttons"])

    return buttons
