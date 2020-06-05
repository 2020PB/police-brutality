import React from 'react';

export default function Hello(props: object): JSX.Element {
    return <h1 {...props} >Hello, World</h1>;
}