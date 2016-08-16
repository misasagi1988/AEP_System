'''
Created on 2016-08-10

@author: Bella_Meng
'''
import sys
sys.path.append("..")
import os
import argparse

def parser_args(argv):
    '''
    parse args from command line
    :param argv: input args from command line
    :return: parse result
    '''
    p = argparse.ArgumentParser(description = "deploy sample and check test result.")
    p.add_argument("-d", "--deploy", action = "store_true", default = False, dest = "deploy_sample",
                   help = "deploy sample")
    p.add_argument("-c", "--check", action = "store",  type = str,  dest = "build_number",
                   help = "check result for build number input")
    p.add_argument("-g", "--get", action = "store", type = str, dest = "get_condition",
                   help = "get sc no detection sample based on condition")
    return p.parse_args(argv)

def main(argv):
    '''
    main func, call different function according to args from cmd
    :param argv: input args from command line
    :return: None
    '''
    r = parser_args(argv)
    if r.deploy_sample:
        import deploy_sample
        deploy_sample.main()
    if r.build_number:
        import check_result
        check_result.main(r.build_number)
    if r.get_condition:
        import get_nodetection_sample
        get_nodetection_sample.main(r.get_condition)


if __name__ == "__main__":
    main(sys.argv[1:])
