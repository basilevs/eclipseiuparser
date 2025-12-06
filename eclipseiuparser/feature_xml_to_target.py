from feature import parse_feature_xml
from sys import argv

def main():
    for i in argv[1:]:
        unit_id, _, _, _ = parse_feature_xml(i)
        feature = unit_id.split(":", 1)[1]
        print(f'<unit id="{feature}.feature.group" version="0.0.0"/>')

if __name__ == '__main__':
    main()