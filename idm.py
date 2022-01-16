# -*- coding: utf-8 -*-

from __future__ import print_function
from time import sleep
from ctypes import *
import sqlite3

dbname = 'pasori.db'
conn = sqlite3.connect(dbname)
cur = conn.cursor()

# libpafe.hの77行目で定義
FELICA_POLLING_ANY = 0xffff

#許可するidm番号を設定
allow_idm_list = ['1234567890123456', '22391CF814021401']

if __name__ == '__main__':

    libpafe = cdll.LoadLibrary("/usr/local/lib/libpafe.so")
    libpafe.pasori_open.restype = c_void_p
    pasori = libpafe.pasori_open()
    libpafe.pasori_init(pasori)
    libpafe.felica_polling.restype = c_void_p
    print("Felicaカードをタッチしてください．")

    try:
        while True:
            sleep(0.1)
            felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
            idm = c_ulonglong() 
            libpafe.felica_get_idm.restype = c_void_p
            libpafe.felica_get_idm(felica, byref(idm))
            idm_No = "%016X" % idm.value
            if idm_No != '0000000000000000':
               cur.execute('SELECT * FROM user WHERE idm = \''+str(idm_No)+'\';')
               userlist = cur.fetchall()
               if len(userlist) != 0:
                  print('こんにちは，{} さん．'.format(userlist[0][1]))
                  print('メニューを選択してください．')
                  print('戻る...................[0]')
                  print('残高のチャージ(入金)...[1]')
                  print('残高の確認.............[2]')
                  print('商品の購入.............[3]')
                  print('新規カードの登録.......[4]')
                  menu = str(input())

                  if menu == '0': #戻る
                     print("戻ります")

                  elif menu == '1': #入金
                     print('金額を入力してください')
                     kingaku = input()
                     cur.execute('UPDATE user SET zandaka = zandaka+'+str(kingaku)+' WHERE idm = \''+str(idm_No)+'\';')
                     conn.commit()
                     cur.execute('SELECT zandaka FROM user WHERE idm =\''+str(idm_No)+'\';')
                     zandakalist=cur.fetchone()
                     print('残高は {} 円です．'.format(zandakalist[0]))

                  elif menu == '2': #残高確認
                     cur.execute('SELECT zandaka FROM user WHERE idm =\''+str(idm_No)+'\';')
                     zandakalist=cur.fetchone()
                     print('残高は {} 円です．'.format(zandakalist[0]))

                  elif menu == '3': #商品購入
                     cur.execute('SELECT * FROM shohin;')
                     shohinlist = cur.fetchall()
                     print('| 商品コード |     商品名    |  商品単価  |')
                     for row in shohinlist:
                        print('| %9s  | %10s | %8s |' % row)
                     print('商品コードを選んでください．')
                     shohin_code = str(input())
                     shohin_code = shohin_code.zfill(3)

                     print(shohin_code)
                     cur.execute('SELECT * FROM shohin WHERE shohin_id=\''+shohin_code+'\';')
                     select_shohinlist=cur.fetchone()

                     if select_shohinlist != None:
                        print('| %9s  | %10s | %8s |' % select_shohinlist)
                        print('この商品を何個購入しますか?(キャンセルの場合は[0])')
                        shohin_kosuu = str(input())

                        cur.execute('UPDATE user SET zandaka = zandaka-'+str(int(shohin_kosuu)*int(select_shohinlist[2]))+' WHERE idm = \''+str(idm_No)+'\';')
                        conn.commit()

                        cur.execute('SELECT zandaka FROM user WHERE idm =\''+str(idm_No)+'\';')
                        zandakalist=cur.fetchone()
                        print('残高は {} 円です．'.format(zandakalist[0]))

                        print('お買い上げありがとうございます．')
                     elif select_shohinlist == None:
                        print('入力された商品コードはデータベースに登録されていません．')

                  elif menu == '4': #新規カード登録
                     print("登録したいFelicaカードをタッチしてください．")
                     while True:
                        sleep(0.1)
                        felica = libpafe.felica_polling(pasori, FELICA_POLLING_ANY, 0, 0)
                        idm = c_ulonglong()
                        libpafe.felica_get_idm.restype = c_void_p
                        libpafe.felica_get_idm(felica, byref(idm))
                        idm_No = "%016X" % idm.value
                        if idm_No != '0000000000000000':
                           cur.execute('SELECT * FROM user WHERE idm = \''+str(idm_No)+'\';')
                           userlist = cur.fetchall()
                           if len(userlist) == 0:
                              print('未登録のFelicaカードを検出しました．')
                              print('IDm {} のFelicaカードを登録しますか?(はい:[1] いいえ:[0])'.format(idm_No))
                              toroku_kakunin = str(input())
                              if toroku_kakunin == '1':
                                 print('ユーザ名を入力してください')
                                 toroku_username =input()
                                 print(toroku_username)
                                 cur.execute('INSERT INTO user (idm,username,zandaka) VALUES (\'' + str(idm_No) + '\',\'' + toroku_username + '\',0);')
                                 conn.commit()
                                 print('登録が完了しました．内容は以下のとおりです．')
                                 cur.execute('SELECT * FROM user WHERE idm =\''+str(idm_No)+'\';')
                                 toroku_naiyou = cur.fetchone()
                                 print('| %9s  | %10s | %8s |' % toroku_naiyou)
                              else :
                                 print('ご利用ありがとうございました．')
                                 break
                           if len(userlist) != 0:
                              print('このFelicaカードは登録済みです．')
                              break
                  print("Felicaカードをタッチしてください")


    except KeyboardInterrupt:
       print('finished')
       libpafe.free(felica)
       libpafe.pasori_close(pasori)
       conn.close()
