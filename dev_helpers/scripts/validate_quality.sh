#!/bin/bash
set -e

echo "Executando testes com coverage..."
TEST_RESULT="OK"
QUALITY_RESULT="OK"
TESTS_OK=false
COVERAGE_OK=false

# Executa os testes
if coverage run --source=apps -m pytest; then
    echo "Testes executados com sucesso"
    TESTS_OK=true
else
    echo "Falha na execução dos testes"
fi

# Verifica a cobertura mínima
if coverage report --fail-under=79; then
    echo "Cobertura mínima de 79% atingida"
    COVERAGE_OK=true
else
    echo "Cobertura abaixo da mínima exigida (mínimo: 79%)"
fi

# Define o resultado final dos testes baseado nos dois critérios
if ! $TESTS_OK || ! $COVERAGE_OK; then
    TEST_RESULT="FALHOU"
    if $COVERAGE_OK && ! $TESTS_OK; then
        echo "Cobertura foi suficiente, mas houve falha nos testes."
    elif $TESTS_OK && ! $COVERAGE_OK; then
        echo "Testes passaram, mas a cobertura não atingiu o mínimo exigido."
    else
        echo "Testes falharam e cobertura insuficiente."
    fi
fi

echo "Executando análise de qualidade com pylint..."

# Códigos habilitados:
# C0301: linha muito longa
# C0302: arquivo com muitas linhas
# W0611: import não usado
# C0410: import desagrupado - imports fora do padrão
# C0411: ordem incorreta dos imports (stdlib, terceiros, locais)
# C0412: import fora do topo do arquivo
# C0413: import depois de código (deve vir no topo)

if pylint $(find . -name "*.py" \
    ! -path "*/migrations/*" \
    ! -path "*/.venv/*" \
    ! -path "*/infra/*" \
    ! -path "*/__pycache__/*" \
    ! -name "manage.py") \
    --disable=all \
    --enable=C0301,C0302,W0611,C0410,C0411,C0412,C0413; then
    echo "Análise de qualidade executada com sucesso"
else
    echo "Falha na análise de qualidade"
    QUALITY_RESULT="FALHOU"
fi


echo ""
echo "==================== RESULTADO FINAL ===================="
echo "TESTES:                        $TEST_RESULT"
echo "QUALIDADE (pylint):            $QUALITY_RESULT"
echo "========================================================="

