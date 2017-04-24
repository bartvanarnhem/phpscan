from enum import Enum

# See Zend/zend_vm_opcodes.h for original definition
ZEND_OPCODE_LIST = [
    'ZEND_NOP',  # 0
    'ZEND_ADD',  # 1
    'ZEND_SUB',  # 2
    'ZEND_MUL',  # 3
    'ZEND_DIV',  # 4
    'ZEND_MOD',  # 5
    'ZEND_SL',  # 6
    'ZEND_SR',  # 7
    'ZEND_CONCAT',  # 8
    'ZEND_BW_OR',  # 9
    'ZEND_BW_AND',  # 10
    'ZEND_BW_XOR',  # 11
    'ZEND_BW_NOT',  # 12
    'ZEND_BOOL_NOT',  # 13
    'ZEND_BOOL_XOR',  # 14
    'ZEND_IS_IDENTICAL',  # 15
    'ZEND_IS_NOT_IDENTICAL',  # 16
    'ZEND_IS_EQUAL',  # 17
    'ZEND_IS_NOT_EQUAL',  # 18
    'ZEND_IS_SMALLER',  # 19
    'ZEND_IS_SMALLER_OR_EQUAL',  # 20
    'ZEND_CAST',  # 21
    'ZEND_QM_ASSIGN',  # 22
    'ZEND_ASSIGN_ADD',  # 23
    'ZEND_ASSIGN_SUB',  # 24
    'ZEND_ASSIGN_MUL',  # 25
    'ZEND_ASSIGN_DIV',  # 26
    'ZEND_ASSIGN_MOD',  # 27
    'ZEND_ASSIGN_SL',  # 28
    'ZEND_ASSIGN_SR',  # 29
    'ZEND_ASSIGN_CONCAT',  # 30
    'ZEND_ASSIGN_BW_OR',  # 31
    'ZEND_ASSIGN_BW_AND',  # 32
    'ZEND_ASSIGN_BW_XOR',  # 33
    'ZEND_PRE_INC',  # 34
    'ZEND_PRE_DEC',  # 35
    'ZEND_POST_INC',  # 36
    'ZEND_POST_DEC',  # 37
    'ZEND_ASSIGN',  # 38
    'ZEND_ASSIGN_REF',  # 39
    'ZEND_ECHO',  # 40
    'ZEND_GENERATOR_CREATE',  # 41
    'ZEND_JMP',  # 42
    'ZEND_JMPZ',  # 43
    'ZEND_JMPNZ',  # 44
    'ZEND_JMPZNZ',  # 45
    'ZEND_JMPZ_EX',  # 46
    'ZEND_JMPNZ_EX',  # 47
    'ZEND_CASE',  # 48
    'ZEND_CHECK_VAR',  # 49
    'ZEND_SEND_VAR_NO_REF_EX',  # 50
    'ZEND_MAKE_REF',  # 51
    'ZEND_BOOL',  # 52
    'ZEND_FAST_CONCAT',  # 53
    'ZEND_ROPE_INIT',  # 54
    'ZEND_ROPE_ADD',  # 55
    'ZEND_ROPE_END',  # 56
    'ZEND_BEGIN_SILENCE',  # 57
    'ZEND_END_SILENCE',  # 58
    'ZEND_INIT_FCALL_BY_NAME',  # 59
    'ZEND_DO_FCALL',  # 60
    'ZEND_INIT_FCALL',  # 61
    'ZEND_RETURN',  # 62
    'ZEND_RECV',  # 63
    'ZEND_RECV_INIT',  # 64
    'ZEND_SEND_VAL',  # 65
    'ZEND_SEND_VAR_EX',  # 66
    'ZEND_SEND_REF',  # 67
    'ZEND_NEW',  # 68
    'ZEND_INIT_NS_FCALL_BY_NAME',  # 69
    'ZEND_FREE',  # 70
    'ZEND_INIT_ARRAY',  # 71
    'ZEND_ADD_ARRAY_ELEMENT',  # 72
    'ZEND_INCLUDE_OR_EVAL',  # 73
    'ZEND_UNSET_VAR',  # 74
    'ZEND_UNSET_DIM',  # 75
    'ZEND_UNSET_OBJ',  # 76
    'ZEND_FE_RESET_R',  # 77
    'ZEND_FE_FETCH_R',  # 78
    'ZEND_EXIT',  # 79
    'ZEND_FETCH_R',  # 80
    'ZEND_FETCH_DIM_R',  # 81
    'ZEND_FETCH_OBJ_R',  # 82
    'ZEND_FETCH_W',  # 83
    'ZEND_FETCH_DIM_W',  # 84
    'ZEND_FETCH_OBJ_W',  # 85
    'ZEND_FETCH_RW',  # 86
    'ZEND_FETCH_DIM_RW',  # 87
    'ZEND_FETCH_OBJ_RW',  # 88
    'ZEND_FETCH_IS',  # 89
    'ZEND_FETCH_DIM_IS',  # 90
    'ZEND_FETCH_OBJ_IS',  # 91
    'ZEND_FETCH_FUNC_ARG',  # 92
    'ZEND_FETCH_DIM_FUNC_ARG',  # 93
    'ZEND_FETCH_OBJ_FUNC_ARG',  # 94
    'ZEND_FETCH_UNSET',  # 95
    'ZEND_FETCH_DIM_UNSET',  # 96
    'ZEND_FETCH_OBJ_UNSET',  # 97
    'ZEND_FETCH_LIST',  # 98
    'ZEND_FETCH_CONSTANT',  # 99
    '_UNASSIGNED_',  # 100
    'ZEND_EXT_STMT',  # 101
    'ZEND_EXT_FCALL_BEGIN',  # 102
    'ZEND_EXT_FCALL_END',  # 103
    'ZEND_EXT_NOP',  # 104
    'ZEND_TICKS',  # 105
    'ZEND_SEND_VAR_NO_REF',  # 106
    'ZEND_CATCH',  # 107
    'ZEND_THROW',  # 108
    'ZEND_FETCH_CLASS',  # 109
    'ZEND_CLONE',  # 110
    'ZEND_RETURN_BY_REF',  # 111
    'ZEND_INIT_METHOD_CALL',  # 112
    'ZEND_INIT_STATIC_METHOD_CALL',  # 113
    'ZEND_ISSET_ISEMPTY_VAR',  # 114
    'ZEND_ISSET_ISEMPTY_DIM_OBJ',  # 115
    'ZEND_SEND_VAL_EX',  # 116
    'ZEND_SEND_VAR',  # 117
    'ZEND_INIT_USER_CALL',  # 118
    'ZEND_SEND_ARRAY',  # 119
    'ZEND_SEND_USER',  # 120
    'ZEND_STRLEN',  # 121
    'ZEND_DEFINED',  # 122
    'ZEND_TYPE_CHECK',  # 123
    'ZEND_VERIFY_RETURN_TYPE',  # 124
    'ZEND_FE_RESET_RW',  # 125
    'ZEND_FE_FETCH_RW',  # 126
    'ZEND_FE_FREE',  # 127
    'ZEND_INIT_DYNAMIC_CALL',  # 128
    'ZEND_DO_ICALL',  # 129
    'ZEND_DO_UCALL',  # 130
    'ZEND_DO_FCALL_BY_NAME',  # 131
    'ZEND_PRE_INC_OBJ',  # 132
    'ZEND_PRE_DEC_OBJ',  # 133
    'ZEND_POST_INC_OBJ',  # 134
    'ZEND_POST_DEC_OBJ',  # 135
    'ZEND_ASSIGN_OBJ',  # 136
    'ZEND_OP_DATA',  # 137
    'ZEND_INSTANCEOF',  # 138
    'ZEND_DECLARE_CLASS',  # 139
    'ZEND_DECLARE_INHERITED_CLASS',  # 140
    'ZEND_DECLARE_FUNCTION',  # 141
    'ZEND_YIELD_FROM',  # 142
    'ZEND_DECLARE_CONST',  # 143
    'ZEND_ADD_INTERFACE',  # 144
    'ZEND_DECLARE_INHERITED_CLASS_DELAYED',  # 145
    'ZEND_VERIFY_ABSTRACT_CLASS',  # 146
    'ZEND_ASSIGN_DIM',  # 147
    'ZEND_ISSET_ISEMPTY_PROP_OBJ',  # 148
    'ZEND_HANDLE_EXCEPTION',  # 149
    'ZEND_USER_OPCODE',  # 150
    'ZEND_ASSERT_CHECK',  # 151
    'ZEND_JMP_SET',  # 152
    'ZEND_DECLARE_LAMBDA_FUNCTION',  # 153
    'ZEND_ADD_TRAIT',  # 154
    'ZEND_BIND_TRAITS',  # 155
    'ZEND_SEPARATE',  # 156
    'ZEND_FETCH_CLASS_NAME',  # 157
    'ZEND_CALL_TRAMPOLINE',  # 158
    'ZEND_DISCARD_EXCEPTION',  # 159
    'ZEND_YIELD',  # 160
    'ZEND_GENERATOR_RETURN',  # 161
    'ZEND_FAST_CALL',  # 162
    'ZEND_FAST_RET',  # 163
    'ZEND_RECV_VARIADIC',  # 164
    'ZEND_SEND_UNPACK',  # 165
    'ZEND_POW',  # 166
    'ZEND_ASSIGN_POW',  # 167
    'ZEND_BIND_GLOBAL',  # 168
    'ZEND_COALESCE',  # 169
    'ZEND_SPACESHIP',  # 170
    'ZEND_DECLARE_ANON_CLASS',  # 171
    'ZEND_DECLARE_ANON_INHERITED_CLASS',  # 172
    'ZEND_FETCH_STATIC_PROP_R',  # 173
    'ZEND_FETCH_STATIC_PROP_W',  # 174
    'ZEND_FETCH_STATIC_PROP_RW',  # 175
    'ZEND_FETCH_STATIC_PROP_IS',  # 176
    'ZEND_FETCH_STATIC_PROP_FUNC_ARG',  # 177
    'ZEND_FETCH_STATIC_PROP_UNSET',  # 178
    'ZEND_UNSET_STATIC_PROP',  # 179
    'ZEND_ISSET_ISEMPTY_STATIC_PROP',  # 180
    'ZEND_FETCH_CLASS_CONSTANT',  # 181
    'ZEND_BIND_LEXICAL',  # 182
    'ZEND_BIND_STATIC',  # 183
    'ZEND_FETCH_THIS',  # 184
    '_UNASSIGNED_',  # 185
    'ZEND_ISSET_ISEMPTY_THIS'  # 186
]


ZEND_OPCODE_LOOKUP = {opcode_name: opcode for opcode, opcode_name in enumerate(ZEND_OPCODE_LIST)}


# See Zend/zend_compile.h for original definition
class OperandType(Enum):
    CONST = 1 << 0
    TMP_VAR = 1 << 1
    VAR = 1 << 2
    UNUSED = 1 << 3
    CV = 1 << 4

OPTYPE_LOOKUP = {optype.value: optype for optype in list(OperandType)}


class Operand(object):

    def __init__(self, var_id, type, data_type, value):
        self._id = var_id
        self._type = OPTYPE_LOOKUP[type]
        self._data_type = data_type
        self._value = value

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def value(self):
        value_typed = self._value

        if self.data_type == 'string':
            pass
        elif self.data_type == 'integer':
            value_typed = int(value_typed)
        # elif self.data_type == 'double':
        #   value_typed = float(value_typed)
        else:
            raise ValueError(
                'Cannot handle operands of type %s' % self.data_type)

        return value_typed

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def data_type(self):
        return self._data_type

    @data_type.setter
    def data_type(self, value):
        self._data_type = value
