def date_slider(self, gid, **kwargs):
    outputs, callbacks, connectors = {}, {}, {}
    # TODO Get key column
    column = "date"
    series = self.data["df"][column]
    num_series = series.apply(lambda x: (x - series.min()).days)

    # TODO Do something with the playback stuff
    button_style = {"width": 100, "height": 50}
    # TODO will need to redo the button stuff (html component wrappers)
    play_id, play = bc.button(gid, "playbutton", "Play/Pause", style=button_style)
    step_id, step_comp = bc.stepper(gid)
    speeds = pd.Series([0, 11])
    speed_id, speed_comp = bc.slider(gid, "speed", speeds, name="speed")
    slider_id, comp = bc.slider(gid, column, num_series, name="date")

    connectors[step_id] = {
        "inputs": [(speed_id, "value"), (play_id, "n_clicks")],
        "outputs": [(step_id, "disabled"), (step_id, "interval")],
    }

    def update_speed(*args):
        ctx = dash.callback_context
        speed_value = 0
        n_clicks = 0
        for inp, value in ctx.inputs.items():
            if "speed" in inp:
                speed_value = value
            if "n_clicks" in inp:
                n_clicks = value

        if speed_value == 0:
            return True, 0
        elif (n_clicks % 2) == 0:
            return True, 2000 / speed_value
        else:
            return False, 2000 / speed_value

    callbacks[step_id] = update_speed

    connectors[slider_id] = {
        "inputs": [(step_id, "n_intervals")],
        "outputs": [(slider_id, "value")],
    }

    def update_time(*args):
        ctx = dash.callback_context
        date_value = 0
        for inp, value in ctx.inputs.items():
            if "n_intervals" in inp:
                date_value = value % num_series.max()
        return date_value

    callbacks[slider_id] = update_time

    outputs[slider_id] = "value"
    return [[step_comp, play, speed_comp], [comp]], outputs, callbacks, connectors
