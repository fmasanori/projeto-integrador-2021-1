import pandas as pd


def citySearch(city, role, csvPaths):
    # CARACTERÍSTICAS GERAIS DO ELEITORADO
    col_list_eleitorado = ["NM_MUNICIPIO", "DS_GRAU_ESCOLARIDADE",
                           "QT_ELEITORES_INC_NM_SOCIAL", "DS_FAIXA_ETARIA",
                           "DS_ESTADO_CIVIL"]

    iter_csv_eleitorado = pd.read_csv(csvPaths[0], usecols=col_list_eleitorado,
                                      delimiter=";", encoding='iso-8859-1',
                                      error_bad_lines=False)

    # Remove a coluna da cidade
    df_result = iter_csv_eleitorado.loc[iter_csv_eleitorado["NM_MUNICIPIO"] == city].drop(
        columns=["NM_MUNICIPIO"], axis=1)

    # Converte para json
    df_result.apply(pd.Series.value_counts, axis=1)

    # Alterações necessárias
    ds_grau_escolaridade_string = df_result["DS_GRAU_ESCOLARIDADE"].value_counts(
    ).to_json()

    ds_estado_civil_string = df_result["DS_ESTADO_CIVIL"].value_counts()
    ds_estado_civil_string = ds_estado_civil_string[:-1].to_json()

    ds_faixa_etaria_string = df_result["DS_FAIXA_ETARIA"].value_counts().to_json()

    ds_faixa_etaria_string = ds_faixa_etaria_string.replace("  ", "")


    col_abstencao = ["NR_TURNO", "NM_MUNICIPIO", 
                 "QT_APTOS", "QT_COMPARECIMENTO", "QT_ABSTENCAO"]

    # DataFrame da abstenção de eleitores
    iter_csv_abstencao = pd.read_csv(csvPaths[2], 
                usecols=col_abstencao,    
                sep=';', 
                encoding='iso-8859-1',
                error_bad_lines=False)

    ds_comparecimento_string = comparecimento_eleitorado(iter_csv_abstencao, city)

    cards_eleitorado = '{' + f'"DS_GRAU_ESCOLARIDADE": {ds_grau_escolaridade_string}, "DS_ESTADO_CIVIL": {ds_estado_civil_string}, "DS_FAIXA_ETARIA": {ds_faixa_etaria_string}, {ds_comparecimento_string}' + '}'

    eleitorado = cards_eleitorado.replace(
        '\n', ' ').replace('\r', '')


    # NOME SOCIAL
    total_eleitores_nomesocial = 0  # Iniciando a variável
    df_nomesocial = df_result.groupby('QT_ELEITORES_INC_NM_SOCIAL')[
        'QT_ELEITORES_INC_NM_SOCIAL'].sum()

    # Somando a quantidade de eleitores com nome social em cada grupo
    for index_nomesocial in range(len(df_nomesocial)):
        total_eleitores_nomesocial += df_nomesocial.index[index_nomesocial] * \
            df_nomesocial.values[index_nomesocial]

    qntString = str(total_eleitores_nomesocial)
    # Gerando string do nome social
    nomeSocial = f'"quantidade": {qntString}'

    # CANDIDATO ELEITO
    # Geração do CSV de candidato
    col_list_candidato = ["NR_TURNO", "NM_UE", "DS_CARGO",
                          "NM_CANDIDATO", "SG_PARTIDO",
                          "DS_SIT_TOT_TURNO"]

    iter_csv_candidato = pd.read_csv(csvPaths[1], usecols=col_list_candidato,
                                     sep=';', encoding='iso-8859-1',
                                     error_bad_lines=False)

    # # Gerando string

    # Verificando cargo desejado e criando query a partir disso
    if role == "GOVERNADOR":
        candidato = iter_csv_candidato.query(
            f'DS_CARGO == "{role}" and DS_SIT_TOT_TURNO == "ELEITO" and NM_UE == "SÃO PAULO"')

    elif role == "PREFEITO":
        candidato = iter_csv_candidato.query(
            f'DS_CARGO == "{role}" and DS_SIT_TOT_TURNO == "ELEITO" and NM_UE == "{city}"')

    else:
        candidato = iter_csv_candidato.query(
            f'DS_CARGO == "{role}" and DS_SIT_TOT_TURNO == "ELEITO"')

    candidato_result = candidato.drop(
        columns=["NM_UE"], axis=1).reset_index(drop=True)
    candidato_result = candidato_result.drop(
        columns=["DS_SIT_TOT_TURNO"], axis=1).squeeze().to_json()

    cards = '{ "cards": [' + eleitorado + '], "cardCandidato": [' + \
        candidato_result + '], "cardNomeSocial": [{' + nomeSocial + '}]}'

    print(cards)
    return cards




def comparecimento_eleitorado(iter_csv, city):
    abstencao_municipio = iter_csv.query(f'NM_MUNICIPIO == "{city.upper()}"')

    # Avaliando abstenções no primeiro turno
    primeiro_turno_data = abstencao_municipio.query('NR_TURNO == 1')
    comparecimento_primeiro_turno = primeiro_turno_data.QT_COMPARECIMENTO.sum()
    abstencao_primeiro_turno = primeiro_turno_data.QT_ABSTENCAO.sum()

    # Avaliando abstenções no segundo turno
    segundo_turno_data = abstencao_municipio.query('NR_TURNO == 2')
    comparecimento_segundo_turno = segundo_turno_data.QT_COMPARECIMENTO.sum()
    abstencao_segundo_turno = segundo_turno_data.QT_ABSTENCAO.sum()

    # Calculando os valores do primeiro turno
    total_eleitores_primeiro_turno = comparecimento_primeiro_turno + abstencao_primeiro_turno
    comparecimento_primeiro_turno_pct = comparecimento_primeiro_turno / total_eleitores_primeiro_turno
    abstencao_primeiro_turno_pct = abstencao_primeiro_turno / total_eleitores_primeiro_turno

    # Calculando os valores do segundo turno
    total_eleitores_segundo_turno = comparecimento_segundo_turno + abstencao_segundo_turno
    comparecimento_segundo_turno_pct = comparecimento_segundo_turno / total_eleitores_segundo_turno
    abstencao_segundo_turno_pct = abstencao_segundo_turno / total_eleitores_segundo_turno

    string_completa = '"QT_COMPARECIMENTO": {"primeiro_turno": '+ str(total_eleitores_primeiro_turno) + ',"segundo_turno":' + str(total_eleitores_segundo_turno) + "}"

    return string_completa


