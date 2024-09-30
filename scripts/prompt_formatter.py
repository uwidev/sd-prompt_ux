"""Enter format prompt."""
import gradio as gr
from modules import script_callbacks, scripts, shared

# from prompt_formatting_pipeline import pipeline
from scripts import prompt_formatting_pipeline as pipeline

"""
Formatting settings
"""
SPACE_COMMAS = True
BRACKET2WEIGHT = True
SPACE2UNDERSCORE = False
IGNOREUNDERSCORES = True

ui_prompts = set()


def format_prompt(*prompts: tuple[dict]):
    sync_settings()

    ret = []

    for component, prompt in prompts[0].items():
        if not prompt or prompt.strip() == "":
            ret.append("")
            continue

        # Clean up the string
        prompt = pipeline.normalize_characters(prompt)
        prompt = pipeline.remove_mismatched_brackets(prompt)

        # Clean up whitespace for cool beans
        prompt = pipeline.remove_whitespace_excessive(prompt)

        # Replace Spaces and/or underscores, unless disabled
        prompt = pipeline.space_to_underscore(prompt, opposite=IGNOREUNDERSCORES)
        prompt = pipeline.align_brackets(prompt)
        prompt = pipeline.space_and(
            prompt
        )  # for proper compositing alignment on colons
        prompt = pipeline.space_bracekts(prompt)
        prompt = pipeline.align_colons(prompt)
        prompt = pipeline.align_commas(prompt, do_it=SPACE_COMMAS)
        prompt = pipeline.align_alternating(prompt)
        prompt = pipeline.bracket_to_weights(prompt, do_it=BRACKET2WEIGHT)

        ret.append(prompt.strip())

    return ret


def on_before_component(component: gr.component, **kwargs: dict):
    elem_id = kwargs.get("elem_id", None)
    if elem_id:
        if elem_id in [
            "txt2img_prompt",
            "txt2img_neg_prompt",
            "img2img_prompt",
            "img2img_neg_prompt",
        ]:
            ui_prompts.add(component)

        elif elem_id == "paste":
            with gr.Blocks(analytics_enabled=False) as ui_component:
                button = gr.Button(value="🪄", elem_classes="tool", elem_id="format")
                button.click(
                    fn=format_prompt,
                    inputs=ui_prompts,
                    outputs=ui_prompts,
                )
                return ui_component

    return None


def on_ui_settings():
    section = ("pformat", "Prompt Formatter")
    shared.opts.add_option(
        "pformat_space_commas",
        shared.OptionInfo(
            True,
            "Add a spaces after comma",
            gr.Checkbox,
            {"interactive": True},
            section=section,
        ),
    )
    shared.opts.add_option(
        "pfromat_bracket2weight",
        shared.OptionInfo(
            True,
            "Convert excessive brackets to weights",
            gr.Checkbox,
            {"interactive": True},
            section=section,
        ),
    )
    shared.opts.add_option(
        "pfromat_space2underscore",
        shared.OptionInfo(
            False,
            "Convert spaces to underscores (default: underscore to spaces)",
            gr.Checkbox,
            {"interactive": True},
            section=section,
        ),
    )
    shared.opts.add_option(
        "pfromat_ignoreunderscores",
        shared.OptionInfo(
            True,
            "Do not convert either spaces or underscores (preserves DanBooru tag formatting)",
            gr.Checkbox,
            {"interactive": True},
            section=section,
        ),
    )

    sync_settings()


def sync_settings():
    global SPACE_COMMAS, BRACKET2WEIGHT, SPACE2UNDERSCORE, IGNOREUNDERSCORES
    SPACE_COMMAS = shared.opts.pformat_space_commas
    BRACKET2WEIGHT = shared.opts.pfromat_bracket2weight
    SPACE2UNDERSCORE = shared.opts.pfromat_space2underscore
    IGNOREUNDERSCORES = shared.opts.pfromat_ignoreunderscores


script_callbacks.on_before_component(on_before_component)
script_callbacks.on_ui_settings(on_ui_settings)
