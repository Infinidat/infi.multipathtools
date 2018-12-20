
from unittest import TestCase, SkipTest
from mock import patch, Mock, MagicMock

#pylint: disable-all

EMPTY_CONFIGURATION = """
defaults {
}
blacklist {
}
blacklist_exceptions {
}
devices {
}
multipaths {
}
""".lstrip('\n')

EMPTY_CONFIGURATION__EMPTY_CHILDREN = """
defaults {
}
blacklist {
    device {
    }
}
blacklist_exceptions {
    device {
    }
}
devices {
    device {
    }
}
multipaths {
    multipath {
    }
}
""".lstrip('\n').replace('    ', '\t')

KEY_VALUE_ITEMS = """
a 1
b "hello 1"
foo legen...|wait.for\wit|[^dary]
""".strip('\n').replace('    ', '\t')

SAMPLE_CONFIGURATIONS = [
    'defaults {\n\tverbosity 2\n\tpolling_interval 5\n\tudev_dir "/dev"\n\tmultipath_dir "/lib64/multipath"\n\tpath_selector "round-robin 0"\n\tpath_grouping_policy failover\n\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\tprio const\n\tfeatures "0"\n\tpath_checker directio\n\tfailback manual\n\trr_min_io 1000\n\trr_weight uniform\n\tqueue_without_daemon yes\n\tpg_timeout none\n\tflush_on_last_del no\n\tuser_friendly_names yes\n\tfind_multipaths no\n\tlog_checker_err always\n}\nblacklist {\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevnode "^(ram|raw|loop|fd|md|dm-|sr|scd|st)[0-9]*"\n\tdevnode "^hd[a-z]"\n\tdevnode "^dcssblk[0-9]*"\n\tdevice {\n\t\tvendor "STK"\n\t\tproduct "Universal Xport"\n\t}\n\tdevice {\n\t\tvendor "DGC"\n\t\tproduct "LUNZ"\n\t}\n\tdevice {\n\t\tvendor "EMC"\n\t\tproduct "LUNZ"\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "S/390.*"\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "S/390.*"\n\t}\n\tdevice {\n\t\tvendor "STK"\n\t\tproduct "Universal Xport"\n\t}\n}\nblacklist_exceptions {\n}\ndevices {\n\tdevice {\n\t\tvendor "NEXSAN"\n\t\tproduct "SATABoy2"\n\t}\n\tdevice {\n\t\tvendor "COMPELNT"\n\t\tproduct "Compellent Vol"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "APPLE*"\n\t\tproduct "Xserve RAID "\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "3PARdata"\n\t\tproduct "VV"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DEC"\n\t\tproduct "HSG80"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker hp_sw\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 hp_sw"\n\t\tprio hp_sw\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "A6189A"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "(COMPAQ|HP)"\n\t\tproduct "(MSA|HSV)1.0.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker hp_sw\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 hp_sw"\n\t\tprio hp_sw\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "(COMPAQ|HP)"\n\t\tproduct "MSA VOLUME"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "(COMPAQ|HP)"\n\t\tproduct "HSV1[01]1|HSV2[01]0|HSV300|HSV4[05]0"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "MSA2[02]12fc|MSA2012i"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 18\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "MSA2012sa|MSA23(12|24)(fc|i|sa)|MSA2000s VOLUME"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 18\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "HSVX700"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "1 alua"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "LOGICAL VOLUME.*"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 12\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "OPEN-.*"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 18\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "HP"\n\t\tproduct "P2000 G3 FC|P2000G3 FC/iSCSI|P2000 G3 SAS|P2000 G3 iSCSI"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 18\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "DDN"\n\t\tproduct "SAN DataDirector"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "EMC"\n\t\tproduct "SYMMETRIX"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --page=pre-spc3-83 --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 6\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DGC"\n\t\tproduct ".*"\n\t\tproduct_blacklist "LUNZ"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker emc_clariion\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 emc"\n\t\tprio emc\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 60\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "EMC"\n\t\tproduct "Invista"\n\t\tproduct_blacklist "LUNZ"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 5\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "FSC"\n\t\tproduct "CentricStor"\n\t\tpath_grouping_policy group_by_serial\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "HITACHI"\n\t\tproduct "OPEN-.*"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\tno_path_retry 6\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "HITACHI"\n\t\tproduct "DF.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio hds\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "ProFibre 4000R"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1722-600"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 300\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1724"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 300\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1726"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 300\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1742"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1745|1746"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1745"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1746"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1814"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1815"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1818"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "3526"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "3542"\n\t\tpath_grouping_policy group_by_serial\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "2105800"\n\t\tpath_grouping_policy group_by_serial\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "2105F20"\n\t\tpath_grouping_policy group_by_serial\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "1750500"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "2107900"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "2145"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "S/390 DASD ECKD"\n\t\tproduct_blacklist "S/390.*"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/sbin/dasdinfo -u -b %n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "S/390 DASD FBA"\n\t\tproduct_blacklist "S/390.*"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/sbin/dasdinfo -u -b %n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "IPR.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "1 alua"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "AIX"\n\t\tproduct "VDASD"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 60\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "3303      NVDISK"\n\t\tpath_grouping_policy failover\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 60\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "AIX"\n\t\tproduct "NVDISK"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "1 alua"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 60\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DELL"\n\t\tproduct "MD3000"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DELL"\n\t\tproduct "MD3000i"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DELL"\n\t\tproduct "MD32xx"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "DELL"\n\t\tproduct "MD32xxi"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "NETAPP"\n\t\tproduct "LUN.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio ontap\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 128\n\t}\n\tdevice {\n\t\tvendor "IBM"\n\t\tproduct "Nseries.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio ontap\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 128\n\t}\n\tdevice {\n\t\tvendor "Pillar"\n\t\tproduct "Axiom.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio alua\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "SGI"\n\t\tproduct "TP9[13]00"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "SGI"\n\t\tproduct "TP9[45]00"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "SGI"\n\t\tproduct "IS.*"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "STK"\n\t\tproduct "OPENstorage D280"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "SUN"\n\t\tproduct "(StorEdge 3510|T4)"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "PIVOT3"\n\t\tproduct "RAIGE VOLUME"\n\t\tpath_grouping_policy multibus\n\t\tgetuid_callout "/lib/udev/scsi_id --page=0x80 --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "1 queue_if_no_path"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 100\n\t}\n\tdevice {\n\t\tvendor "SUN"\n\t\tproduct "CSM200_R"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "SUN"\n\t\tproduct "LCSM100_[IEFS]"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "(LSI|ENGENIO)"\n\t\tproduct "INF-01-00"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "2 pg_init_retries 50"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry 15\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "STK"\n\t\tproduct "FLEXLINE 380"\n\t\tproduct_blacklist "Universal Xport"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker rdac\n\t\tfeatures "0"\n\t\thardware_handler "1 rdac"\n\t\tprio rdac\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\tno_path_retry queue\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "EUROLOGC"\n\t\tproduct "FC2502"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --page=0x80 --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker directio\n\t\tfeatures "0"\n\t\thardware_handler "0"\n\t\tprio const\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n\tdevice {\n\t\tvendor "NEC"\n\t\tproduct "DISK ARRAY"\n\t\tpath_grouping_policy group_by_prio\n\t\tgetuid_callout "/lib/udev/scsi_id --whitelisted --device=/dev/%n"\n\t\tpath_selector "round-robin 0"\n\t\tpath_checker tur\n\t\tfeatures "0"\n\t\thardware_handler "1 alua"\n\t\tprio alua\n\t\tfailback immediate\n\t\trr_weight uniform\n\t\trr_min_io 1000\n\t}\n}\nmultipaths {\n}',
                         ]

class OutputTests(TestCase):
    def test_output__empty_configuration(self):
        from . import Configuration
        config = Configuration()
        self.assertEqual(config.to_multipathd_conf(), EMPTY_CONFIGURATION)

    def test_output__empty_configuration__everything_is_none(self):
        from . import Configuration, Device, MultipathEntry, HardwareEntry
        config = Configuration()
        config.blacklist.device.append(Device())
        config.whitelist.device.append(Device())
        config.multipaths.append(HardwareEntry())
        config.devices.append(MultipathEntry())
        self.assertEqual(config.to_multipathd_conf(), EMPTY_CONFIGURATION__EMPTY_CHILDREN)

from re import compile, DOTALL, MULTILINE
from . import KEY_VALUE_PATTERN, MULTIPATH_CONF_PATTERN

from os.path import exists, join, sep, abspath, dirname
from pkg_resources import resource_filename
SAMPLE_FILEPATH = resource_filename(__name__, "sample.txt")


class InputTests(TestCase):
    def test_empty_configuration(self):
        from . import Configuration
        config = Configuration.from_multipathd_conf(EMPTY_CONFIGURATION)

    def test_samples(self):
        from . import Configuration
        pattern = compile(MULTIPATH_CONF_PATTERN, DOTALL | MULTILINE)
        for sample in SAMPLE_CONFIGURATIONS:
            matches = pattern.match(sample)
            config = Configuration.from_multipathd_conf(sample)

    def test_regex__empty_configuration(self):
        pattern = compile(MULTIPATH_CONF_PATTERN, DOTALL | MULTILINE)
        matches = [match.groupdict() for match in pattern.finditer(EMPTY_CONFIGURATION)]
        sections = [dict['name'] for dict in matches]
        self.assertIn('defaults', sections)
        self.assertIn('blacklist', sections)
        self.assertIn('blacklist_exceptions', sections)
        self.assertIn('devices', sections)
        self.assertIn('multipaths', sections)

    def test_regex__key_value_pattern(self):
        pattern = compile(KEY_VALUE_PATTERN, DOTALL | MULTILINE)
        result = pattern.search("key value")
        self.assertEqual(result.groupdict()['key'], 'key')
        self.assertEqual(result.groupdict()['value'], 'value')
        result = pattern.search(r"regex ^this|is|[a][^complicated](regex).*/")
        self.assertEqual(result.groupdict()['key'], 'regex')
        self.assertEqual(result.groupdict()['value'], '^this|is|[a][^complicated](regex).*/')

    def test_regex__multiple_key_values(self):
        pattern = compile(KEY_VALUE_PATTERN, DOTALL | MULTILINE)
        iterator = pattern.finditer(KEY_VALUE_ITEMS)

        expected_keys = ['a', 'b', 'foo']
        expected_values = ['1', '"hello 1"', "legen...|wait.for\wit|[^dary]"]
        for match in iterator:
            self.assertEqual(len(list(match.groupdict().keys())), 2)
            self.assertIn(match.groupdict()['key'], expected_keys)
            self.assertIn(match.groupdict()['value'], expected_values)

    def test_populate_munch(self):
        from . import populate_munch_from_multipath_conf_string
        from munch import Munch
        string = """
            foo bar
            high lower
            1 0
            """.replace('    ', '\t')
        instance = Munch()
        populate_munch_from_multipath_conf_string(instance, string)
        self.assertEqual(instance.foo, 'bar')
        self.assertEqual(instance.high, 'lower')
        self.assertEqual(instance['1'], '0')

    def test_rulelist_from_string(self):
        from . import RuleList
        string = """
        devnode ^something%N
        devnode else$
        wwid 010203040506
        device {
            product someProduct
            vendor someVendor
        }
        """.replace('    ', '\t')
        instance = RuleList.from_multipathd_conf(string)
        self.assertEqual(len(instance.device), 1)
        self.assertEqual(len(instance.devnode), 2)
        self.assertEqual(len(instance.wwid), 1)
        self.assertEqual(instance.device[0].product, 'someProduct')
        self.assertEqual(instance.device[0].vendor , 'someVendor')
        self.assertEqual(instance.devnode, ['^something%N', 'else$'])
        self.assertEqual(instance.wwid, ['010203040506', ])


    def test_regex__sample_configuration(self):
        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)

        pattern = compile(MULTIPATH_CONF_PATTERN, DOTALL | MULTILINE)
        matches = [match.groupdict() for match in pattern.finditer(sample_config_string)]
        sections = [dict['name'] for dict in matches]
        self.assertIn('defaults', sections)
        self.assertIn('blacklist', sections)
        self.assertIn('blacklist_exceptions', sections)
        self.assertIn('devices', sections)
        self.assertIn('multipaths', sections)

    def test_sample_configuration(self):
        from . import Configuration

        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)

        config = Configuration.from_multipathd_conf(sample_config_string)
        self.assertEqual(config.attributes.udev_dir, '/dev')
        self.assertEqual(config.attributes.polling_interval, '10')
        self.assertEqual(config.attributes.uid, '0')
        self.assertEqual(config.blacklist.wwid, ['26353900f02796769'])
        self.assertIn('"^dcssblk[0-9]*"', config.blacklist.devnode)
        self.assertEqual(config.blacklist.device[0].product, "MSA[15]00")
        self.assertIn('"IBM.75000000092461.4d00.36"', config.whitelist.wwid)
        self.assertEqual(len(config.devices), 2)
        self.assertEqual(config.multipaths[0].wwid, "3600508b4000156d700012000000b0000")
        self.assertEqual(config.multipaths[0].failback, "manual")
        self.assertEqual(len(config.multipaths), 2)
        self.assertEqual(config.devices[1].path_grouping_policy, "multibus")

class InOut(TestCase):
    def test_sample_configuration(self):
        raise SkipTest
        from . import Configuration

        assert exists(SAMPLE_FILEPATH)
        with open(SAMPLE_FILEPATH, 'r') as fd:
            sample_config_string = fd.read()
        assert len(sample_config_string)
        config = Configuration.from_multipathd_conf(sample_config_string)
        self.assertEqual(config.to_multipathd_conf(), sample_config_string)
