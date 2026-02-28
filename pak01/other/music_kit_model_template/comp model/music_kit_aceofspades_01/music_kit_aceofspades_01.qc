// Created by Crowbar 0.74

$modelname "inventory_items\music_kits\cc\music_kit_aceofspades_01.mdl"

$bodygroup "studio"
{
	studio "music_kit.smd"
}

$surfaceprop "default"

$contents "solid"

$illumposition -0.047 0.731 0.538

$cdmaterials "models\inventory_items\music_kit\cc\aceofspades_01\"
$cdmaterials "models\inventory_items\music_kit\"

$cbox 0 0 0 0 0 0

$bbox -2.443 -1.602 0 0.982 1.509 1.075

$definebone "kit_root" "" 0 0 0 0 0 0 0 0 0 0 0 0


$sequence "ref" {
	"music_kit_aceofspades_01_anims\ref.smd"
	fadein 0.2
	fadeout 0.2
	fps 30
}

$keyvalues
{
// CSGO compiler adds the qc_path keyvalue section automatically.
//	qc_path 
//	{
//		"value" "models\inventory_items\music_kit\cc\aceofspades_01.qc"
//	}
}
