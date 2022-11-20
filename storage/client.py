
# * This block of code MUST be executed first.  
# _______________________________________________________
# import os
# import sys
# from pathlib import Path
# path_root      = Path(__file__).parent.absolute()
# (path_root, _) = os.path.split(path_root)
# sys.path.append(str(path_root))
# print(sys.path)
# _______________________
import socket as S
from storage.doa.parameters import PutParameters,GetParameters
import uuid 
import numpy as np
import json
import hashlib
import time

class Client(object):
    def __init__(self,**kwargs):
        self.client_id = str(uuid.uuid4())
        self.hostname  = kwargs.get("hostname","localhost")
        self.port      = kwargs.get("port",3000)
        self.INT_BYTES    = 1
        self.USIZE_BYTES  = 8
        self.TOKENS       = {
            "PUT":1,
            "GET": 2,
        }
        self.socket = S.socket(S.AF_INET,S.SOCK_STREAM)
        self.socket.connect((self.hostname,self.port))
    def __recvall(self,socket, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = socket.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    
    def __check_integrity(**kwargs):
        _bytes              = kwargs.get("_bytes")
        metadata_checksum   = kwargs.get("checksum")
        checksum            = hashlib.sha256(_bytes).hexdigest()
        return checksum == metadata_checksum



    def get(self,**kwargs):
        CMD_BYTES    = self.TOKENS["GET"].to_bytes(self.INT_BYTES, "big")
        socket = self.socket
        # SEND CMD.
        socket.sendall(CMD_BYTES)
        # SEND GET-PARAMETERS.
        parameters   = kwargs.get("params",GetParameters(
            id = kwargs.get("id"),
            _from = kwargs.get("_from",None)
        )).to_json()
        params_bytes = bytes(parameters,encoding="utf8")
        params_size  = len(params_bytes)
        # SEND PARAMS SIZE 
        socket.sendall(params_size.to_bytes(self.USIZE_BYTES,"big"))
        # SEND PARAMS.
        socket.sendall(params_bytes)
        # READ METADATA SIZE
        response_size_bytes = self.__recvall(socket,self.USIZE_BYTES)
        # print("RESPONSE_SIZE_BYTES {}".format(response_size_bytes))
        response_size       = int.from_bytes(response_size_bytes,"big")
        # print("RESPONSE_SIZE {}".format(response_size))
        response_bytes      = self.__recvall(socket,response_size).decode("utf8")
        response      = json.loads(response_bytes)
        # print("RESPONSE ", response)
        # READ BYTES
        bytes_size    = response["metadata"]["size"]
        _bytes        = self.__recvall(socket,bytes_size)
        # ____________________________________________________
        # 
        # prese
        # checksum      = hashlib.sha256(_bytes).hexdigest()
        # preversed_integrity = checksum == response["metadata"]["checksum"]
        preversed_integrity = Client.__check_integrity(_bytes=_bytes, checksum= response["metadata"]["checksum"])
        
        # print("METADATA_CHECKSUM {}".format(response["metadata"]["checksum"]))
        # print("CLIENT_CHECKSUM {}".format(checksum))
        # print("PREVERSED_INTEGRITY {}".format(preversed_integrity))
        if not preversed_integrity:
            raise Exception("INTEGRITY ISSUE")

        return response,_bytes

    def get_matrix(self,**kwargs):
        # Get metadata and bytes
        response, _bytes = self.get(**kwargs)
        # Extract tags (shape and dtype)
        tags             = response["metadata"]["tags"]
        # Interpret shape 
        shape            = eval(tags["shape"])
        # Extract dtype
        dtype            = tags["dtype"]
        # Get matrix using bytes, shape and dtype
        matrix           = np.frombuffer(_bytes,dtype=dtype).reshape(shape)
        return response,matrix
        
    
    def put(self,**kwargs):
        try:
            _bytes         = kwargs.get("_bytes")
            parameters       = kwargs.get("parameters",
            PutParameters(
                id = "ball-{}".format(str(uuid.uuid4())[:4] ),
                size = len(_bytes),
                client_id = self.client_id )
            ).to_json()
            # _______________________________________________
            # CMD          = 1
            CMD_BYTES    = self.TOKENS["PUT"].to_bytes(self.INT_BYTES, "big")
            # print("CMD_BYTES {}".format(CMD_BYTES))
            params_bytes = bytes(parameters,encoding="utf8")
            params_size  = len(params_bytes)
            # print("PARAMS_SIZE {}".format(params_size))
            # _______________________________________________
            # with S.socket(S.AF_INET,S.SOCK_STREAM) as socket:
            socket = self.socket
            # socket.connect((self.hostname,self.port))
            # SEND CMD.
            socket.sendall(CMD_BYTES)
            # SEND PARAMS LEN.
            socket.sendall(params_size.to_bytes(self.USIZE_BYTES,"big"))
            # SEND PARAMS.
            socket.sendall(params_bytes)
            # SEND BYTES.
            socket.sendall(_bytes)
            # READ RESPONSE BYTES.
            response_size = int.from_bytes(self.__recvall(socket,self.USIZE_BYTES),"big")
            # READ RESPONSE AN DECODE AS STRING.
            response      = self.__recvall(socket,response_size).decode("utf8")
            print(response)
            return json.loads(response)
            # _______________________________________________
        except Exception as e:
            print(e)

    def put_matrix(self,**kwargs):
        try:
            matrix           = kwargs.get("matrix",np.array([]))
            _bytes           = matrix.tobytes()
            matrix_id_suffix = str(uuid.uuid4())[:4]
            checksum         = hashlib.sha256(_bytes).hexdigest()

            put_parmeters         = PutParameters(
                id        = kwargs.get("id","matrix-{}".format(matrix_id_suffix )), 
                size      = len(_bytes),
                client_id = self.client_id,
                checksum  = checksum,
                tags      = {
                    "dtype":str(matrix.dtype) ,
                    "shape": str(matrix.shape)
                }
            )
            # print(put_parmeters.to_json())
            self.put(
                _bytes = _bytes,
                parameters = put_parmeters,
            )

        except Exception as e :
            print(e)

            

            # s.sendall(b"WRITE")



if __name__ == "__main__":
    c1 = Client(
        hostname = "localhost",
        port = 6000
    )

    # big_matrix = np.random.random((11,11,3))
    # c1.put_matrix(id = "matrix-0",matrix = big_matrix)
    # print("_"*40)
    start = time.time()

    for i in range(10):
        c1.get_matrix(id = "matrix-0")
        print("_"*40)
    st = time.time() - start
    print("EXECUTION_TIME ",st)
    # c1.get(id = "matrix-0")
    # print("_"*40)
    # c1.get(id = "matrix-0")
    # print("_"*40)
    # c1.get(id = "matrix-0")
    # print("_"*40)
    # c1.get(id = "matrix-0")
    # c1.get(id = "matrix-ba63")
    # c1.get(id = "matrix-ba63")
    # c1.put(_bytes   = b"n")
    # put_0 = c1.put_matrix(matrix = np.array([[1,2],[3,4]]))
    # print(put_0)
    # c1.put_matrix(id = "matrix-1",matrix = big_matrix)
    # c1.put_matrix(id = "matrix-2",matrix = big_matrix)
    # c1.put_matrix(matrix = big_matrix)