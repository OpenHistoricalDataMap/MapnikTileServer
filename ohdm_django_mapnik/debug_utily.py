import subprocess
from config.settings.base import env


def get_style_xml(generate_style_xml: bool) -> str:
    if generate_style_xml:
        return subprocess.run("carto {}/project.mml 1>&2".format(
            env("CARTO_STYLE_PATH")
        ),
            cwd=env("CARTO_STYLE_PATH"),
            shell=True, stderr=subprocess.PIPE).stderr.decode("utf-8")
    else:
        return open("{}/style.xml".format(env("CARTO_STYLE_PATH")), 'r', encoding="utf-8").read()
