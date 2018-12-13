import sys
from ctypes import windll
from pathlib import Path

k32 = windll.LoadLibrary('kernel32.dll')
setConsoleModeProc = k32.SetConsoleMode
setConsoleModeProc(k32.GetStdHandle(-11), 0x0001 | 0x0002 | 0x0004)
# import winreg
#
# winreg.SetValueEx(winreg.HKEY_CURRENT_USER,r'HKEY_CURRENT_USER\Console\VirtualTerminalLevel',0,winreg.REG_DWORD,1)
import MDL
import ValveUtils
from ValveUtils import GameInfoFile, KeyValueFile

if __name__ == '__main__':
    # model = Path(r"G:\SteamLibrary\SteamApps\common\half-life 2\hl2\models\shadertest\envballs.mdl")
    model = Path(sys.argv[1])
    # if len(sys.argv) > 2:
    #     dump_path = Path(sys.argv[2])
    # else:
    #     dump_path = None
    mod_path = ValveUtils.get_mod_path(model)
    game_info_path = mod_path / 'gameinfo.txt'
    if not game_info_path.exists():
        raise FileNotFoundError("Failed to find gameinfo file")
    gi = GameInfoFile(game_info_path)
    # mod_paths = gi.get_search_paths_recursive()
    textures = []
    materials = []
    other_files = []
    print('Searching in:')
    for path in gi.get_search_paths_recursive():
        print('\x1b[92m{}\x1b[0m'.format(path))
    if model.exists():
        other_files.append(model)
        mdl = MDL.SourceMdlFile49(filepath=str(model.with_name(model.stem)), read=False)
        mdl.read_skin_families()
        mdl.read_texture_paths()
        mdl.read_textures()
        # print(mdl.file_data.textures)
        for texture in mdl.file_data.textures:
            for tex_path in mdl.file_data.texture_paths:
                mat = gi.find_material(Path(tex_path) / texture.path_file_name, use_recursive=True)
                if mat:
                    temp = ValveUtils.get_mod_path(mat).parent
                    materials.append((Path(mat), Path(mat).relative_to(temp)))
            ...

        for mat in materials:
            kv = KeyValueFile(mat[0])
            for v in list(kv.as_dict.values())[0].values():
                if '/' in v or '\\' in v:
                    tex = gi.find_texture(v, True)
                    if tex:
                        temp = ValveUtils.get_mod_path(tex).parent
                        textures.append((Path(tex), Path(tex).relative_to(temp)))
            # print(kv.as_dict)
        for texture in mdl.file_data.textures:
            exist = False
            found_path = None
            for mat in materials:
                mat = mat[1]
                if mat.stem == texture.path_file_name:
                    exist = True
                    found_path = mat
                    break
            if exist:
                print('>>>\033[94m', texture.path_file_name, '-> \033[92mFound here \033[0m>', '\033[95m', found_path,
                      '\033[0m')
            else:
                print('>>>\033[94m', texture.path_file_name, '-> \033[91mNot found!', '\033[0m')

    textures = list(set(textures))
    input('Press Enter to exit')
    # print('*'*10,'MATERIALS','*'*10)
    # pprint(materials)
    # print('*'*10,'TEXTURES','*'*10)
    # pprint(textures)