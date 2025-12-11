@echo off
echo Running MusicVAE 16-bar interpolations for all stories...
echo.

echo ===================================================================
echo === CARNIVAL ===
echo ===================================================================
echo.

echo Running carnival 1to2 (9 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/carnival/config_1to2.json
echo.

echo Running carnival 3to4 (12 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/carnival/config_3to4.json
echo.

echo ===================================================================
echo === LANTERN ===
echo ===================================================================
echo.

echo Running lantern 1to2 (3 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/lantern/config_1to2.json
echo.

echo Running lantern 2to3 (3 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/lantern/config_2to3.json
echo.

echo Running lantern 3to4 (18 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/lantern/config_3to4.json
echo.

echo ===================================================================
echo === STARLING_FIVE ===
echo ===================================================================
echo.

echo Running starling_five 1to2 (2 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/starling_five/config_1to2.json
echo.

echo Running starling_five 2to3 (3 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/starling_five/config_2to3.json
echo.

echo Running starling_five 3to4 (9 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/starling_five/config_3to4.json
echo.

echo ===================================================================
echo === WINDOW_BLUE_CURTAIN ===
echo ===================================================================
echo.

echo Running window_blue_curtain 1to2 (12 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/window_blue_curtain/config_1to2.json
echo.

echo Running window_blue_curtain 2to3 (3 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/window_blue_curtain/config_2to3.json
echo.

echo Running window_blue_curtain 3to4 (7 outputs)...
music_vae_generate --json_config=cluster_nearest_neighbors/window_blue_curtain/config_3to4.json
echo.

echo ===================================================================
echo All interpolations complete!
echo ===================================================================
pause
