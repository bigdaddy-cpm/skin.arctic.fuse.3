"""Offline checks and deterministic Kodi packaging; no Kodi installation is modified."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[1]
SKIN_ID = 'skin.arctic.fuse.3.bigdaddy'


def validate():
    manifest = ET.parse(ROOT / 'addon.xml').getroot()
    assert manifest.attrib['id'] == SKIN_ID
    assert manifest.attrib['name'] == 'Arctic Fuse 3 (BigDaddy)'
    assert 'jurialmunkey' in manifest.attrib['provider-name']
    assert 'jamal2362' in manifest.attrib['provider-name']
    imports = {node.attrib['addon']: node.attrib for node in manifest.findall('requires/import')}
    assert imports['xbmc.gui']['version'] == '5.18.0'
    assert imports['script.skinvariables']['version'] == '2.2.18'
    assert imports['script.texturemaker']['version'] == '0.2.9'
    assert imports['plugin.video.themoviedb.helper']['version'] == '6.21.5'
    assert imports['resource.images.arctic.splash']['optional'] == 'true'
    assert imports['resource.images.arctic.splash']['version'] == '1.1.0'
    assert imports['resource.images.arctic.weather']['optional'] == 'true'
    assert imports['resource.images.arctic.weather']['version'] == '1.0.4'
    assert manifest.find("extension[@point='xbmc.addon.metadata']/license").text == 'Creative Commons Attribution Non-Commercial Share-Alike 4.0'
    assert (ROOT / 'LICENSE.txt').is_file()
    count_xml = count_json = 0
    for folder in ('1080i', 'shortcuts', 'colors', 'fonts'):
        for path in (ROOT / folder).rglob('*'):
            if path.suffix not in ('.xml', '.json', '.xmltemplate'):
                continue
            text = path.read_text(encoding='utf-8-sig')
            assert not re.search(r'(?m)^(<<<<<<< |=======\s*$|>>>>>>> )', text), path
            assert not re.search(r'skin\.arctic\.fuse\.3(?!\.bigdaddy)', text), path
            assert 'rebootfromnand' not in text, path
            assert 'RebootToAndroid' not in text, path
            if path.suffix == '.xmltemplate':
                continue  # Generator fragments are not standalone XML documents.
            if path.suffix == '.json':
                json.loads(text)
                count_json += 1
                continue
            tree = ET.fromstring(text)
            count_xml += 1
            for include in tree.findall('.//include[@file]'):
                filename = include.attrib['file']
                if '$' in filename or filename.startswith(('script-skinvariables-', 'script-skinshortcuts-')):
                    continue
                assert (ROOT / '1080i' / filename).is_file(), (path, filename)
    generator = json.loads((ROOT / 'shortcuts/skinvariables-generator.json').read_text())
    assert generator['skinid'] == SKIN_ID
    for entry in generator['genxml']:
        assert (ROOT / 'shortcuts' / entry['datafile']).is_file(), entry
    # New hub menus must stay in this fork's settings namespace and retain
    # the existing hub identities, names, paths and enabled/disabled state.
    paths = ET.parse(ROOT / '1080i/Includes_Paths.xml')
    namespace = paths.find("variable[@name='Path_SkinVariables_SkinFolder']")
    assert all((node.text or '').startswith(SKIN_ID) for node in namespace.findall('value'))
    migration = json.loads((ROOT / 'shortcuts/skinvariables-migrate-hubs.json').read_text())
    expected_hubs = {'1101', '1102', '1103', '1104', '1106', '1107', '1108', '1109'}
    assert {item['window'] for item in migration['menu']} == expected_hubs
    for item in migration['menu']:
        window = item['window']
        assert item['slot'] == window[-2:]
        for key in ('label', 'icon', 'path', 'target', 'disabled'):
            assert item[key] == '{%s_%s}' % (key, window)
        for key, suffix in (('name', 'Name'), ('icon', 'Icon'), ('path', 'Shortcut.Path'),
                            ('target', 'Shortcut.Target'), ('toggle', 'Toggle')):
            assert migration['infolabels'][key + '_' + window] == 'Skin.String(HomeSwitcher.%s.%s)' % (window, suffix)
    custom_dialog = ET.parse(ROOT / '1080i/Dialog_DialogCustom.xml')
    assert not any((node.text or '').strip() in (
        'DialogCustom_Settings_Items_ColourPresets', 'DialogCustom_Settings_Items_ColourHighlights')
        for node in custom_dialog.findall('.//include'))
    # The new wizard must not automatically reconfigure existing installations.
    startup = json.loads((ROOT / 'shortcuts/skinvariables-startup.json').read_text())
    wizard_rules = []
    def visit_actions(value, rules=()):
        if isinstance(value, dict):
            rules = rules + tuple(value.get('rules', ()))
            for key, child in value.items():
                if key != 'rules':
                    visit_actions(child, rules)
        elif isinstance(value, list):
            for child in value:
                visit_actions(child, rules)
        elif value == 'Skin.SetBool(SetupWizard.Pending)':
            wizard_rules.append(rules)
    visit_actions(startup)
    assert wizard_rules and all('!Skin.HasSetting(DefaultConfig.InitDone)' in rules for rules in wizard_rules)
    # Piers builds settings in SkinVariables. Keep the entry point, search,
    # category/group links and native radiobutton state intact after merging.
    settings_entry = ET.parse(ROOT / '1080i/SkinSettings.xml')
    assert 'RunScript(script.skinvariables,run_skinsettings=special://skin/shortcuts/skinvariables-skinsettings.json)' in [
        node.text for node in settings_entry.findall('onload')]
    settings_template = ET.parse(ROOT / '1080i/script-skinvariables-skinsettings.xml')
    templates = {node.findtext('description'): node for node in settings_template.findall('.//include')
                 if node.find('description') is not None}
    assert templates['Setting Radiobutton'].find("param[@name='control']").text == 'radiobutton'
    assert templates['Search Edit'].find("param[@name='id']").text == '12'
    skinsettings = json.loads((ROOT / 'shortcuts/skinvariables-skinsettings.json').read_text())
    assert skinsettings['search']['mode'] == 'global'
    for key, group in skinsettings['groups'].items():
        assert group['category'] in skinsettings['categories'], key
    for key, setting in skinsettings['settings'].items():
        assert setting['group'] in skinsettings['groups'], key
        assert setting['label'] and setting['onclick'], key
        assert setting['control'] in ('button', 'radiobutton'), key
        if setting['control'] == 'radiobutton':
            assert setting['selected'], key
    # Full home-screen presets overwrite widgets, so retain upstream's explicit
    # yes/no confirmation; startup must never apply these presets automatically.
    actions = ET.parse(ROOT / '1080i/Includes_Actions.xml')
    preset = actions.find("include[@name='Action_SetupWizard_WidgetPreset']")
    confirmation = preset.findtext('definition/onclick')
    assert 'run_dialog=yesno' in confirmation and '$LOCALIZE[31848]' in confirmation
    assert 'skinvariables-setupwizard-preset.json' in confirmation
    assert 'skinvariables-setupwizard-preset.json' not in json.dumps(startup)
    settings_info = ET.parse(ROOT / '1080i/Includes_Settings.xml')
    assert any(SKIN_ID in (node.text or '') for node in settings_info.findall(".//param[@name='fallback']"))
    assert (ROOT / 'extras/backgrounds/blur/coal_blur.jpg').is_file()
    background = ET.parse(ROOT / '1080i/Includes_Background.xml')
    seasonal = [node for node in background.findall('.//include')
                if (node.text or '').strip() == 'Background_StartUp_SelectedScene']
    assert len(seasonal) == 1
    assert seasonal[0].attrib['condition'] == '!$EXP[Exp_StartUp_CustomImage] + System.AddonIsEnabled(resource.images.arctic.splash)'
    fallback = next(node for node in background.findall('.//control')
                    if node.findtext('texture') == 'special://skin/extras/backgrounds/blur/coal_blur.jpg')
    assert '!System.AddonIsEnabled(resource.images.arctic.splash)' in fallback.findtext('visible')
    assert '!$EXP[Exp_StartUp_CustomImage]' in fallback.findtext('visible')
    scenes = ET.parse(ROOT / '1080i/Includes_StartUp_Scenes.xml')
    selected = scenes.find("include[@name='Background_StartUp_SelectedScene']/definition")
    assert {node.text for node in selected.findall('include')} == {
        'Background_StartUp_Scene_Tokyo', 'Background_StartUp_Scene_Countryside',
        'Background_StartUp_Layered'}
    weather = ET.parse(ROOT / '1080i/Includes_Weather.xml')
    artwork = weather.find("include[@name='Weather_Card_Artwork']/definition")
    assert artwork.findtext('control/visible') == '!System.AddonIsEnabled(resource.images.arctic.weather)'
    assert all('System.AddonIsEnabled(resource.images.arctic.weather)' in node.attrib['condition']
               for node in artwork.findall('include'))
    settings = ET.parse(ROOT / '1080i/Settings.xml')
    assert any(node.text == 'RunAddon(service.libreelec.settings)' for node in settings.findall('.//onclick'))
    assert not (ROOT / '.github/workflows/dispatch_to_repo.yml').exists()
    ppi = ET.parse(ROOT / '1080i/Includes_U3k.xml').find("include[@name='PPI_Button']")
    button = ppi.find("control[@id='6009']")
    actions = button.findall('onclick')
    assert actions[1].text == 'RunScript(script.bigdaddy.playbackinfo)'
    assert actions[1].attrib['condition'] == 'System.AddonIsEnabled(script.bigdaddy.playbackinfo)'
    assert actions[2].text == 'RunScript(script.tinyppi,dialog)'
    assert actions[2].attrib['condition'].startswith('!System.AddonIsEnabled(script.bigdaddy.playbackinfo) + ')
    assert button.findtext('visible') == 'System.AddonIsEnabled(script.bigdaddy.playbackinfo) | System.AddonIsEnabled(script.tinyppi)'
    assert ppi.find("include/param[@name='visible']").text == button.findtext('visible')
    assert (ROOT / 'extras/icons/sysinfo.png').is_file()
    nav = ET.parse(ROOT / '1080i/VideoOSD.xml').find(".//control[@id='6091']")
    assert nav.find("onleft[.='6009']").attrib['condition'] == button.findtext('visible')
    assert nav.find("onleft[.='6008']").attrib['condition'] == '!System.AddonIsEnabled(script.bigdaddy.playbackinfo) + !System.AddonIsEnabled(script.tinyppi)'
    process = ET.parse(ROOT / '1080i/Dialog_DialogProcessInfo.xml')
    dv = process.find("include[@name='DialogProcessInfo_Items_DVObject']/definition/item")
    assert 'DV.Enhanced' in dv.findtext('visible')
    assert '!String.IsEmpty($PARAM[info])' in dv.findtext('visible')
    rows = process.findall(".//include[@content='DialogProcessInfo_Items_DVObject']")
    assert len(rows) == 8
    gpu = next(row for row in rows if row.find("param[@name='info']").text.endswith('(DV.GPURender)'))
    assert 'condition' not in gpu.attrib
    assert 'DV.GPUAvailable' in gpu.find("param[@name='visible']").text
    expected_properties = {'Mode', 'Display', 'Transport', 'Profile', 'FEL', 'GPURender', 'TVProfile', 'SignalIntent'}
    assert {row.find("param[@name='info']").text for row in rows} == {
        'Window(playerprocessinfo).Property(DV.%s)' % prop for prop in expected_properties}
    strings = (ROOT / 'language/resource.language.en_gb/strings.po').read_text(encoding='utf-8')
    for label in range(31980, 31988):
        assert strings.count('msgctxt "#%d"' % label) == 1
    print('Validated %d XML and %d JSON files, identity, dependencies and fallback paths.' % (count_xml, count_json))
    return manifest


def build(manifest):
    output = ROOT / 'dist' / ('%s-%s.zip' % (SKIN_ID, manifest.attrib['version']))
    output.parent.mkdir(exist_ok=True)
    files = sorted(path for path in ROOT.rglob('*') if path.is_file()
                   and not any(part in ('.git', '.github', 'tools', 'dist', '__pycache__')
                               for part in path.relative_to(ROOT).parts)
                   and path.name not in ('.gitignore', '.gitattributes') and path.suffix != '.pyc')
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            name = SKIN_ID + '/' + path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            data = path.read_bytes()
            if path.suffix in ('.xml', '.json', '.po', '.md', '.txt'):
                data = data.replace(b'\r\n', b'\n')
            archive.writestr(info, data)
    with zipfile.ZipFile(output) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist()) == len(set(archive.namelist()))
        assert ET.fromstring(archive.read(SKIN_ID + '/addon.xml')).attrib == manifest.attrib
        assert all(name.startswith(SKIN_ID + '/') and '..' not in name.split('/')
                   for name in archive.namelist())
        assert SKIN_ID + '/media/Textures.xbt' in archive.namelist()
        assert SKIN_ID + '/media/u3k/discart.png' in archive.namelist()
    print('Built %s (%d files, %d bytes)' % (output, len(files), output.stat().st_size))
    print('SHA256: ' + hashlib.sha256(output.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    manifest = validate()
    if args.build:
        build(manifest)
