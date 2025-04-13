CREATE OR REPLACE VIEW vw_produtos_indexados as 
select 
    pr.productid as id,
    pr.name,
    pr.productnumber,
    pr.color,
    pr.listprice as list_price,
    pr.size,
    pr.weight,
    pr.safetystocklevel as stock_level,
    pr.productmodelid as product_model_id
from production.product as pr 
left join production.productmodel as pm on pr.productmodelid = pm.productmodelid
where pr.name is not null and pr.listprice <> 0;