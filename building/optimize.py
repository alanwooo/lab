import os
import sys
import json
import argparse

price_apartment_avg = 3450
price_basement = 1800
price_garage = 78000
house = {
# wang
'F' : (258.54, 7, 1123231),
# wu
'E' : (257.78, 7, 1060944),
}
more_area_price = {
5  : 3450,
10 : 1.1 * 3450,
20 : 1.2 * 3450,
1000 : 4650,
}
apart_type = { 
'3#' : { 
        'D2' : (131.55, '3-2-1', 'Edge'),
        'E2' : (118.22, '3-2-1', 'Middle'),
        'E3' : (119.18, '3-2-1', 'Middle'),
        'F' : (156.47, '4-2-2', 'Middle'),
       },
'9#' : {
        'J' : (155.06, '4-2-2', 'Edge'),
        'K' : (137.56, '3-2-2', 'Middle'),
       },
# 12# or 8#
'8#': {
        'C1' : (148.53, '3-2-2', 'Edge'),
        'A1' : (109.05, '3-2-1', 'Middle'),
        'B' : (86.81, '3-2-1', 'Middle'),
        'D2' : (135.53, '3-2-1', 'Middle'),
       },
# 4# or 5#
'4#' : {
        'C2' : (145.76, '3-2-2', 'Edge, two balcony'),
        'E1' : (120.65, '3-2-1', 'Middle'),
        'E3' : (118.64, '3-2-1', 'Middle'),
        'F1' : (155.76, '4-2-2', 'Middle, two balcony'),
        'D2' : (131.55, '3-2-1', 'Edge'),
        'E2' : (118.22, '3-2-1', 'Middle'),
        'E4' : (119.18, '3-2-1', 'Middle'),
        'F2' : (156.47, '4-2-2', 'Middle, two balcony'),
       },
}
price_per_floor = {
'4#' : (3, 17, 33, -150),
'3#' : (3, 17, 33, -150),
# 5# or 8# or 12#
'8#' : (2, 17, 33, -150),
# 9#
'9#' : (1, 16, 33, -160),
}



def calculate_price(apt, sel, bs, gar):
    print apt
    hou = house[sel]
    f_low = 0
    apt_area = 0
    for b, t, f, _, _ in apt:
        apt_area += apart_type[b][t][0]
        if f == 33:
            continue
        f_low = f if f > f_low else f_low

    # If the area of the apartments is more the replacement area of the house,
    # the price of per square meter is more expensive.
    # 0 < more area <= 5, per square meter is 3450 * 1
    # 5 < more area <= 10, per square meter is 3450 * 1.1
    # 10 < more area <= 20, per square meter is 3450 * 1.2
    # 20 < more area, per square meter is 4650
    rate = 0
    replace_area = hou[0]# + 7
    mr = round(apt_area - replace_area, 3)
    if 0 < mr <= 5:
        rate = 1
    elif 5 < mr <= 10:
        rate = 1.1
    elif 10 < mr <= 20:
        rate = 1.2

    # We assume that the 7 square meter is free for us. Also we always add
    # the exceeding area to the low floor apartment, since this can help
    # to save money. 
    total = 0
    flag = True
    flag_s = True
    rest_area = 0
    #replace_area -= 7
    for i, (b, t, f, _, _) in enumerate(apt):
        price_floor = price_per_floor[b][3] if f == price_per_floor[b][2] else (f - price_per_floor[b][1]) * 10
        if replace_area > 0:
            replace_area -= apart_type[b][t][0]
        print mr, i, replace_area, f, flag, rate, flag_s, price_floor, price_per_floor
        if f_low == f and flag:
            flag = False
            # Calculate the high floor apartment price, the 7 square meter should
            # give to the high floor. Since the low floor should have low price.
            mon = (apart_type[b][t][0] - 7) * (3450 + price_floor)
        else:
            # mr is the exceeding area, if mr < 0, the we did not need to buy exceeding area.
            if mr > 0:
                if replace_area <= 0 and flag_s:
                    # rate == 0 means the exceeding area is greater than 20 squre area.
                    if rate == 0:
                        mon = (apart_type[b][t][0] - (0 - replace_area)) * (3450 + price_floor)  + (0 - replace_area) * (4650 + price_floor)
                    else:
                        mon = (apart_type[b][t][0] - (0 - replace_area)) * (3450 + price_floor) + (0 - replace_area) * (3450 * rate + price_floor)
                    flag_s = False
                elif not flag_s:
                    if rate == 0:
                       mon = apart_type[b][t][0] * (4650 + price_floor)
                    else:
                       mon = apart_type[b][t][0] * (3450 * rate + price_floor)
                else:
                    mon = apart_type[b][t][0] * (3450 + price_floor)
            else:
                mon = apart_type[b][t][0] * (3450 + price_floor)
        total += mon
        apt[i][4] = round(mon, 3)

    # basement
    if bs:
        total += price_basement * bs

    # garge
    if gar:
        total += price_garage * gar

    # return a tuple (rest memory, exceeding area, basement, garge, select apartment, house, )
    return (hou[2] - total, mr, bs, gar, apt, hou,) 

def print_result(info):
    print '**************************************************************Details************************************************************************'
    print 'Replacement Area: %s\tTotal Price: %s\t Free Area: %s\t' % (info[5][0], info[5][2], info[5][1])
    print '\n'
    print 'Selected Apartments:'
    for i, (b, t, f, o, m) in enumerate(info[4]): 
        print '\t%d.\tBuiding No: %-6sAlias: %-6sType: %-8sFloor: %-6sArea: %-8sTotal Memory: %-10sComments: %s' % (i + 1, o, t, apart_type[b][t][1],f, apart_type[b][t][0], m, apart_type[b][t][2])
    if info[2]:
        print '\n'
        print 'Basement Area: %-6s\tTotal Memory: %s' % (info[2], price_basement * info[2])
    if info[3]:
        print 'Garge Number: %-6s\tTotal Memory: %s' % (info[3], price_garage * info[3])
    print '\n'
    print 'Exceed Area: %s' % info[1]
    print '\n'
    print 'Rest Memory: %s' % info[0]
    print '*********************************************************************************************************************************************'

def main():
    parser = argparse.ArgumentParser(usage='optimize.py -s [F/E] -u Size -g Number -a Building:Type:Floor,Building:Type:Floor,...')
    parser.add_argument('-a', '--apartment', type=str, required=True, help='The aparment which you want to select. Format Building:Type:Floor,Building:Type:Floor,...')
    parser.add_argument('-s', '--select', type=str, required=True, help='F is front house, E is end house.')
    parser.add_argument('-b', '--basement', type=int, help='The basement area(square meter) which you want to buy.')
    parser.add_argument('-g', '--garage', type=int, help='The garage number which you want to buy.')
    args = parser.parse_args()

    selected = []
    apart = args.apartment
    if ':' in apart:
        if ',' in apart:
            apart = apart.split(',')
        apart = [apart] if isinstance(apart, str) else apart
        for item in apart:
            if item.count(':') != 2:
                print 'Format Building:Type:Floor, Building:Type:Floor,...'
                return False

            bld, tp, flo = item.split(':')
            bld_old = str(bld) + '#'
            if bld in ['8', '12']:
                bld = '8#'
            elif bld in ['4', '5']:
                bld = '4#'
            elif bld in ['3', '9']:
                bld = str(bld) + '#'
            else:
                print 'Building Number is 3/4/5/8/9/12.'
                return False

            flo = int(flo) if flo else 17
            if flo > 33 or (bld in ['3#', '9#'] and flo < 1) or (bld == '8#' and flo < 2) \
                or (bld == '4#' and flo < 3):
                print bld, tp, flo
                print 'Building\t\tvalid floor\n',\
                      '3#, 4#\t\t\t3 - 33\n', \
                      '5#, 8#, 12#\t\t2 - 33\n', \
                      '9#\t\t\t1 - 33'
                return False

            #print  bld, tp, flo, apart_type[bld], apart_type[bld].has_key(tp)
            if not apart_type[bld].has_key(tp):
                print 'The building %s only has the apartment type %s' % (bld_old, ','.join(apart_type[bld].keys()))
                return False
            #[building number, type, floor number, old building number, total memory]
            selected.append([bld, tp, int(flo), bld_old, 0])
    else:
        print 'Format Building:Type:Floor, Building:Type:Floor,...'
        return False

    # Floor 33 is very cheap
    selected = sorted(selected, key=lambda selected:selected[2] if selected[2] != 33 else 0, reverse=True)
    #print select, bld_old
    sel = args.select
    if sel not in ['F', 'E']:
        print 'Valid host is F or E'

    bs = args.basement
    gar = args.garage

    print_result(calculate_price(selected, sel, bs, gar))
if __name__ == '__main__':
    main()
