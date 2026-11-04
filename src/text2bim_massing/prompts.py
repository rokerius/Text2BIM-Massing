"""Explicit adaptations of preserved Text2BIM prompts, without editing the originals."""

from importlib.resources import files

SOURCE_NAMES = {
    "Enhancer": "po_chat_prompt_temp.txt",
    "Programmer": "coder_chat_prompt_temp.txt",
    "Reviewer": "checker_chat_prompt_temp.txt",
    "Architect": "floor_plan_designer_chat_prompt_few_shots.txt",
}

ARCHITECT_MASSING_EXAMPLE = '''Here is a sample conversation:
"""
User: I want to build an office building. I want the building to have 3 floors and the layout of each floor to be the same. Use a {width}{unit} x {depth}{unit} footprint and a {height}{unit} floor height.
Architect: **3-Floor Office Building Design**

**Massing Footprint:**
- Rectangular profile: (0,0), ({width},0), ({width},{depth}), (0,{depth}).

**Extrusion:**
- Bottom elevation: 0{unit}. Top elevation: {top}{unit}.
- The three floor levels share the same footprint.

**Summary:**
- Building dimensions: {width}{unit} x {depth}{unit} x 3 floors, as requested.
"""

'''


def load_prompts(units="mm") -> dict[str, str]:
    if units not in {"m", "mm"}:
        raise ValueError("Prompt units must be m or mm")
    root = files("text2bim_massing._vendor.text2bim").joinpath("prompts")
    prompts = {role: root.joinpath(name).read_text() for role, name in SOURCE_NAMES.items()}
    prompts["Enhancer"] = (
        prompts["Enhancer"]
        .replace("in Vectorworks", "in the massing scene")
        .replace("plan_desinger", "plan_designer")
    )
    prompts["Reviewer"] = prompts["Reviewer"].replace("in Vectorworks", "in the massing scene")
    prompts["Reviewer"] = prompts["Reviewer"].replace(
        "Issues are listed in the form of bullet points. Each issue contains a description and list of uuids of the corresponding elements in the generated building model.",
        "Issues are a JSON record containing the task, current scene and immutable candidates with actual external evaluation reports.",
    )
    prompts["Reviewer"] = prompts["Reviewer"].replace(
        "Reviewer: ",
        'Return only JSON: {"action":"improve" or "finish", "candidate_id":"an evaluated archive ID", "guidance":"your review and patch instructions"}. '
        "Select the candidate according to the task and actual reports. Report fields have no implicit optimization direction; do not invent a score.\nReviewer: ",
    )
    prompts["Programmer"] = prompts["Programmer"].replace(
        "If necessary, you can import and use the Python standard library.",
        "Only public math imports and the documented builtins are available. Private attributes, filesystem access and other imports are unavailable.",
    )
    prompts["Programmer"] = prompts["Programmer"].replace(
        "Now, based on the conversation given below",
        "Each script is transactional: an execution error rolls back ALL its scene edits and variables; previously successful scripts remain. "
        "After building or editing, call candidate_id = commit_candidate(), report = evaluate(candidate_id), and select_candidate(candidate_id). "
        "An evaluation applies only to that snapshot. Reuse an archived report by evaluate(candidate_id); selection never re-evaluates it. "
        "Profiles and extrusions have independent geometry. Do not create walls, slabs, doors, windows or story layers.\n"
        "Now, based on the conversation given below",
    )
    # Preserve role, rationality instruction, few-shot format and task insertion.
    # The example adapts the source three-floor office to supported massing tools.
    architect = prompts["Architect"]
    prompts["Architect"] = architect[: architect.index("Depending on")]
    prompts["Architect"] += (
        "Describe massing footprints, holes, detached components and extrusion elevations in structured text. "
        "Respect the site and external task context. Give coordinates and dimensions; functional requirements "
        "should guide volumes rather than BIM components.\n\n"
        + architect[
            architect.index("Make your design") : architect.index("Here is a sample conversation:")
        ]
        + ARCHITECT_MASSING_EXAMPLE.format(
            width=30000 if units == "mm" else 30,
            depth=15000 if units == "mm" else 15,
            height=3000 if units == "mm" else 3,
            top=9000 if units == "mm" else 9,
            unit=units,
        )
        + architect[architect.index("The user now provides") :]
    )
    if units == "m":
        prompts = {
            role: value.replace("millimeter units", "meter units")
            for role, value in prompts.items()
        }
    return prompts
