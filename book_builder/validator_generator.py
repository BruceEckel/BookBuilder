from validate import Validator

def create_validation_command(validator):
    function_string = f"""
@validate.command()
@click.option('--trace', default="")
def {validator.command_name}(trace):
    "{validator.__doc__.strip()}"
    click.echo(_validate.Validator.one_check({validator.name()}, trace))

"""
    return function_string


if __name__ == '__main__':
    for v in [v("") for v in Validator.__subclasses__()]:
        print(create_validation_command(v))
