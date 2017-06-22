atom_package_names = {
    '00_Front.md': '',
    '01_How_to_Use_This_Book.md': '',
    '02_Introduction.md': '',
    '03_Installing_Kotlin_and_the_Book_Examples.md': '',
    '04_Running_Kotlin.md': '',
    '05_Comments.md': '',
    '06_Variables.md': 'variables',
    '07_Data_Types.md': 'datatypes',
    '08_Functions.md': 'functions',
    '09_If_Expressions.md': 'ifexpressions',
    '10_String_Templates.md': 'stringtemplates',
    '11_Number_Types.md': 'numbertypes',
    '12_Booleans.md': 'booleans',
    '13_For_Loops.md': 'forloops',
    '14_Ranges.md': 'ranges',
    '15_Expressions_and_Statements.md': 'expressionsandstatements',
    '16_Classes_and_Objects.md': 'classesandobjects',
    '17_Creating_Classes.md': 'creatingclasses',
    '18_KotlinDoc.md': 'kotlindoc',
    '19_Methods_In_Classes.md': 'methodsinclasses',
    '20_Imports_and_Packages.md': 'importsandpackages',
    '21_Testing.md': 'testing',
    '22_Properties.md': 'properties',
    '23_Lists.md': 'lists',
    '24_More_Conditionals.md': 'moreconditionals',
    '25_When_Expressions.md': 'whenexpressions',
    '26_Class_Arguments.md': 'classarguments',
    '27_Named_and_Default_Arguments.md': 'namedanddefault',
    '28_Overloading.md': 'overloading',
    '29_Constructors.md': 'constructors',
    '30_Secondary_Constructors.md': 'secondaryconstructors',
    '31_Class_Exercises.md': 'classexercises',
    '32_Data_Classes.md': 'dataclasses',
    '33_Parameterized_Types.md': 'parameterizedtypes',
    '34_Lambdas.md': 'lambdas',
    '35_map_and_reduce.md': 'mapandreduce',
    '36_Comprehensions.md': 'comprehensions',
    '37_When_Expressions_and_Smart_Casts.md': 'whenexpressionscasts',
    '38_When_Expressions_and_Data_Classes.md': 'whenexpressionsdata',
    '39_Brevity.md': 'brevity',
    '40_A_Bit_of_Style.md': 'bitofstyle',
    '41_Idiomatic_Kotlin.md': 'idiomatic',
    '42_Defining_Operators.md': 'definingoperators',
    '43_Automatic_String_Conversion.md': 'automaticstring',
    '44_Tuples.md': 'tuples',
    '45_Companion_Objects.md': 'companionobjects',
    '46_Inheritance.md': 'inheritance',
    '47_Base_Class_Initialization.md': 'baseclassinit',
    '48_Overriding_Methods.md': 'overridingmethods',
    '49_Enumerations.md': 'enumerations',
    '50_Abstract_Classes.md': 'abstractclasses',
    '51_Traits.md': 'traits',
    '52_Uniform_Access_and_Setters.md': 'uniformaccess',
    '53_Reaching_into_Java.md': 'reachingjava',
    '54_Applications.md': 'applications',
    '55_A_Little_Reflection.md': 'reflection',
    '56_Polymorphism.md': 'polymorphism',
    '57_Composition.md': 'composition',
    '58_Using_Traits.md': 'usingtraits',
    '59_Tagging_Traits_and_Case_Objects.md': 'taggingtraits',
    '60_Type_Parameter_Constraints.md': 'typeparameterconstraints',
    '61_Building_Systems_with_Traits.md': 'buildingwithtraits',
    '62_Lists_and_Recursion.md': 'listsrecursion',
    '63_Combining_Lists_with_zip.md': 'combininglists',
    '64_Sets.md': 'sets',
    '65_Maps.md': 'maps',
    '66_References_and_Mutability.md': 'referencesmutability',
    '67_More_About_When_Expressions.md': 'morewhen',
    '68_Error_Handling_with_Exceptions.md': 'exceptions',
    '69_Constructors_and_Exceptions.md': 'constructorexceptions',
    '70_Error_Reporting_with_Either.md': 'either',
    '71_Handling_Non_Values_with_Option.md': 'option',
    '72_Converting_Exceptions_with_Try.md': 'convertingexceptions',
    '73_Custom_Error_Reporting.md': 'customerrors',
    '74_Design_by_Contract.md': 'dbc',
    '75_Logging.md': 'logging',
    '76_Extension_Methods.md': 'extensionmethods',
    '77_Extensible_Systems_with_Type_Classes.md': 'extensiblesystems',
    '78_Where_to_Go_Now.md': 'wheretogo',
    '79_Appendix_A_AtomicTest.md': 'atomictest',
    '80_Appendix_B_Calling_Kotlin_from_Java.md': 'callingfromjava',
    '81_Copyright.md': ''
}


if __name__ == '__main__':
    """
    Rebuilds the dictionary after you've renumbered the Markdown files.
    Right now you have to paste the results in by hand.
    """
    import config
    new_dict = {}
    not_found = []
    md_names = sorted([f.name for f in config.markdown_dir.glob("[0-9][0-9]_*.md")])
    plain_names = [nm[3:] for nm in md_names]

    def find_name(name):
        plain = name[3:]
        for k in atom_package_names:
            if plain in k:
                new_dict[name] = atom_package_names[k]
                return "old: {}, new: {}".format(k, name)
        not_found.append(name)
        return "{} Not found".format(name)

    for name in md_names:
        print(find_name(name))

    import pprint
    pprint.pprint(new_dict)

    if not_found:
        for nf in not_found:
            print("NOT FOUND: {}".format(nf))
