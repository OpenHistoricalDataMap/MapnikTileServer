import os.path
import subprocess


def create_style_xml(carto_style_path: str):
    """
    create style.xml through carto project.mml
    :return:
    """
    subprocess.run(
        "carto project.mml > style.xml",
        cwd=carto_style_path,
        shell=True,
        stderr=subprocess.PIPE,
    )


def get_style_xml(generate_style_xml: bool, carto_style_path: str) -> str:
    """

    :param generate_style_xml:
    :return:
    """
    if generate_style_xml:
        return subprocess.run(
            "carto {}/project.mml 1>&2".format(carto_style_path),
            cwd=carto_style_path,
            shell=True,
            stderr=subprocess.PIPE,
        ).stderr.decode("utf-8")
    else:

        if not os.path.isfile("{}/style.xml".format(carto_style_path)):
            # create style.xml if not exists
            create_style_xml(carto_style_path=carto_style_path)

        return open(
            "{}/style.xml".format(carto_style_path), "r", encoding="utf-8"
        ).read()
