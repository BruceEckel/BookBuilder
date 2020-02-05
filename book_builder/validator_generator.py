from pathlib import Path
from validate import Validator


def create_validation_command(validator):
    function_string = f"""
@validate.command()
@click.option('--trace', default="")
def {validator.command_name}(trace):
    \"\"\"
    {validator.__doc__.strip()}
    \"\"\"
    click.echo(_validate.Validator.one_check(_validate.{validator.name()}, trace))

"""
    return function_string


if __name__ == '__main__':
    cmds = "".join([create_validation_command(v("")) for v in Validator.__subclasses__()])
    Path("generated_validators.py").write_text(cmds)
