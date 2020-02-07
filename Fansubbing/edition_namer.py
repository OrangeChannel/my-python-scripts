import shlex

header = r'<?xml version="1.0"?>' + '\n' + r'<!-- <!DOCTYPE Tags SYSTEM "matroskatags.dtd"> -->'
header += '\n<Tags>'

editionuids = input('input the edition uids (2906622092 4906785091): ')
uids = list(map(int, editionuids.split()))
names = shlex.split(input('input the edition names (\'normal\' \'no credits\'): '))
outfile = str(input('desired file name (example.xml): '))

if '.xml' not in outfile:
    outfile += '.xml'

tag = ''
for i,n in zip(uids, names):
    tag += '\n\t<Tag>\n'
    tag += '\t\t<Targets>\n'
    tag += '\t\t\t<EditionUID>{}</EditionUID>\n'.format(i)
    tag += '\t\t\t<TargetTypeValue>50</TargetTypeValue>\n'
    tag += '\t\t</Targets>\n'
    tag += '\t\t<Simple>\n'
    tag += '\t\t\t<Name>TITLE</Name>\n'
    tag += '\t\t\t<String>{}</String>\n'.format(n)
    tag += '\t\t\t<TagLanguage>eng</TagLanguage>\n'
    tag += '\t\t\t<DefaultLanguage>1</DefaultLanguage>\n'
    tag += '\t\t</Simple>\n'
    tag += '\t</Tag>'

final = header + tag + '\n</Tags>\n'

file = open(outfile, 'w')
file.write(final)
file.close()
