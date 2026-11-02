"""Case-local variable definitions and user reference configuration."""
from flask import jsonify, request
from variable_reference import describe_variable, save_reference


def metadata(item, case_path):
    result = dict(item, **describe_variable(item['name'], item.get('units',''),
                                          item.get('long_name_en', item.get('long_name','')), case_path))
    result['long_name_en'] = item.get('long_name_en', item.get('long_name',''))
    result['long_name'] = result['zh_name']
    return result


def register_variable_routes(app, context):
    """context returns case_path, busy, lock, lookup(name) -> native metadata."""
    def reference():
        ctx=context()
        with ctx['lock']:
            ctx=context()
            if not ctx.get('case_path'):
                return jsonify(error='请先选择案例'),400
            data=request.get_json(silent=True) or {}
            name=data.get('name') if request.method=='POST' else request.args.get('var')
            if not isinstance(name,str) or not name:
                return jsonify(error='请选择变量'),400
            if ctx.get('busy'):
                return jsonify(error='模型或率定运行中，请等待完成后查看或修改参考'),409
            item=ctx['lookup'](name)
            if item is None:
                return jsonify(error='当前结果中不存在该变量'),404
            if request.method=='POST':
                units=data.get('units',data.get('unit',''))
                if str(units).strip()!=str(item.get('units','')).strip():
                    return jsonify(error='参考单位必须与当前变量的原生输出单位一致'),400
                try:
                    save_reference(ctx['case_path'],name,data,expected_units=item.get('units',''))
                except (ValueError,TypeError) as error:
                    return jsonify(error=str(error)),400
                except OSError as error:
                    return jsonify(error='无法保存本案例参考：'+str(error)),500
            return jsonify(variable=metadata(item,ctx['case_path']))
    app.add_url_rule('/api/results/reference','results_reference',reference,methods=['POST'])
    app.add_url_rule('/api/results/variable_info','results_variable_info',reference,methods=['GET'])
