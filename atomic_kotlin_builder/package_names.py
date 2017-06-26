atom_package_names = {
    '00_Front.md': '',
    '01_How_to_Use_This_Book.md': '',
    '02_Introduction.md': '',
    '03_Installing_Kotlin_and_the_Book_Examples.md': '',
    '04_Running_Kotlin.md': '',
    '05_Comments.md': '',
    '06_Hello_World.md': 'helloworld',
    '07_Variables.md': 'variables',
    '08_Data_Types.md': 'datatypes',
    '09_Functions.md': 'functions',
    '10_If_Expressions.md': 'ifexpressions',
    '11_String_Templates.md': 'stringtemplates',
    '12_Number_Types.md': 'numbertypes',
    '13_Booleans.md': 'booleans',
    '14_For_and_While_Loops.md': 'forandwhile',
    '15_Ranges.md': 'ranges',
    '16_Expressions_And_Statements.md': 'expressionsandstatements',
    '17_Summary_1.md': 'summary1',
    '18_Classes_and_Objects.md': 'classesandobjects',
    '19_Creating_Classes.md': 'creatingclasses',
    '20_KotlinDoc.md': 'kotlindoc',
    '21_Methods_In_Classes.md': 'methodsinclasses',
    '22_Imports_and_Packages.md': 'importsandpackages',
    '23_Testing.md': 'testing',
    '24_Properties.md': 'properties',
    '25_Lists.md': 'lists',
    '26_Summary_2.md': 'summary2',
    '27_When_Expressions.md': 'whenexpressions',
    '28_Class_Arguments.md': 'classarguments',
    '29_Named_and_Default_Arguments.md': 'namedanddefault',
    '30_Overloading.md': 'overloading',
    '31_Constructors.md': 'constructors',
    '32_Secondary_Constructors.md': 'secondaryconstructors',
    '33_Class_Exercises.md': 'classexercises',
    '34_Data_Classes.md': 'dataclasses',
    '35_Extension_Functions.md': 'extensionfunctions',
    '36_Parameterized_Types.md': 'parameterizedtypes',
    '37_Lambdas.md': 'lambdas',
    '38_map_and_reduce.md': 'mapandreduce',
    '39_Comprehensions.md': 'comprehensions',
    '40_When_Expressions_and_Smart_Casts.md': 'whenexpressionscasts',
    '41_When_Expressions_and_Data_Classes.md': 'whenexpressionsdata',
    '42_Brevity.md': 'brevity',
    '43_A_Bit_of_Style.md': 'bitofstyle',
    '44_Idiomatic_Kotlin.md': 'idiomatic',
    '45_Defining_Operators.md': 'definingoperators',
    '46_Automatic_String_Conversion.md': 'automaticstring',
    '47_Tuples.md': 'tuples',
    '48_Companion_Objects.md': 'companionobjects',
    '49_Inheritance.md': 'inheritance',
    '50_Base_Class_Initialization.md': 'baseclassinit',
    '51_Overriding_Methods.md': 'overridingmethods',
    '52_Enumerations.md': 'enumerations',
    '53_Abstract_Classes.md': 'abstractclasses',
    '54_Traits.md': 'traits',
    '55_Uniform_Access_and_Setters.md': 'uniformaccess',
    '56_Reaching_into_Java.md': 'reachingjava',
    '57_Applications.md': 'applications',
    '58_A_Little_Reflection.md': 'reflection',
    '59_Polymorphism.md': 'polymorphism',
    '60_Composition.md': 'composition',
    '61_Using_Traits.md': 'usingtraits',
    '62_Tagging_Traits_and_Case_Objects.md': 'taggingtraits',
    '63_Type_Parameter_Constraints.md': 'typeparameterconstraints',
    '64_Building_Systems_with_Traits.md': 'buildingwithtraits',
    '65_Lists_2.md': 'lists2',
    '66_Lists_and_Recursion.md': 'listsrecursion',
    '67_Combining_Lists_with_zip.md': 'combininglists',
    '68_Sets.md': 'sets',
    '69_Maps.md': 'maps',
    '70_References_and_Mutability.md': 'referencesmutability',
    '71_More_About_When_Expressions.md': 'morewhen',
    '72_Error_Handling_with_Exceptions.md': 'exceptions',
    '73_Constructors_and_Exceptions.md': 'constructorexceptions',
    '74_Error_Reporting_with_Either.md': 'either',
    '75_Handling_Non_Values_with_Option.md': 'option',
    '76_Converting_Exceptions_with_Try.md': 'convertingexceptions',
    '77_Custom_Error_Reporting.md': 'customerrors',
    '78_Design_by_Contract.md': 'dbc',
    '79_Logging.md': 'logging',
    '80_Extension_Methods.md': 'extensionmethods',
    '81_Extensible_Systems_with_Type_Classes.md': 'extensiblesystems',
    '82_Where_to_Go_Now.md': 'wheretogo',
    '83_Appendix_A_AtomicTest.md': 'atomictest',
    '84_Appendix_B_Calling_Kotlin_from_Java.md': 'callingfromjava',
    '85_Copyright.md': ''
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
