SELECT S.relname FROM pg_class AS S
            INNER JOIN pg_depend AS D ON S.oid = D.objid
            INNER JOIN pg_class AS T ON D.refobjid = T.oid
            INNER JOIN pg_attribute AS C ON D.refobjid = C.attrelid AND D.refobjsubid = C.attnum
            INNER JOIN pg_namespace N ON N.oid = S.relnamespace
            WHERE S.relkind = 'S' AND N.nspname = 'cb'
            ORDER BY S.relname